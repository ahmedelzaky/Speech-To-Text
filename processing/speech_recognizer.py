from .audio_visualizer import visualize_audio
from .audio_processor import find_noise_profile, process_chunk
import librosa
import noisereduce as nr
import soundfile as sf
import torch
from uuid import uuid4

# chose the model : "wav2vec" or "whisper"
ASR_MODEL = "whisper"
model = None
processor = None

if ASR_MODEL == "wav2vec":
    from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
    processor = Wav2Vec2Processor.from_pretrained(
        "facebook/wav2vec2-base-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
elif ASR_MODEL == "whisper":
    from transformers import WhisperProcessor, WhisperForConditionalGeneration
    processor = WhisperProcessor.from_pretrained("openai/whisper-small")
    model = WhisperForConditionalGeneration.from_pretrained(
        "openai/whisper-small")
    model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(
        language="en", task="transcribe")

if torch.cuda.is_available():
    model.to("cuda")
else:
    print("CUDA not available, using CPU")


def speech_to_text(chunk, sample_rate, noise_profile=None):
    """Processes an audio chunk through the selected ASR pipeline"""
    if ASR_MODEL == "wav2vec":
        text = process_chunk(chunk, sample_rate, processor, model)
    elif ASR_MODEL == "whisper":
        inputs = processor(
            chunk,
            sampling_rate=sample_rate,
            return_tensors="pt"
        )

        with torch.no_grad():
            generated_ids = model.generate(inputs["input_features"])
            text = processor.batch_decode(
                generated_ids, skip_special_tokens=True, target_lang="en"
            )[0]
    print(f"Transcription ({len(text)} characters): {text}")
    return text


def split_audio_on_silence(audio_file):
    """Splits the audio into chunks based on silence and processes it"""
    audio, sample_rate = librosa.load(
        audio_file, sr=16000, res_type='kaiser_best', mono=True
    )
    print(f"Total duration: {len(audio)/sample_rate:.2f} seconds")

    # Reduce noise
    reduced_noise = nr.reduce_noise(
        y=audio,
        sr=sample_rate,
        prop_decrease=0.8,
    )
    visualize_audio(audio, sample_rate,
                    f"{audio_file.split('.')[0]}_original.png")
    visualize_audio(reduced_noise, sample_rate,
                    f"{audio_file.split('.')[0]}_denoised.png")
    print("Noise reduction applied")
    sf.write(
        f"{audio_file.split('.')[0]}_denoised.wav",
        reduced_noise,
        sample_rate
    )

    # Detect speech segments
    intervals = librosa.effects.split(
        reduced_noise,
        top_db=25,
        frame_length=2048,
        hop_length=512,
    )
    print(f"Found {len(intervals)} speech segments")

    chunks = [reduced_noise[start:end] for start, end in intervals]

    return chunks, sample_rate
