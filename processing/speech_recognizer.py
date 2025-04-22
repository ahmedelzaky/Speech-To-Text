import librosa
import noisereduce as nr
import soundfile as sf
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from .audio_processor import find_noise_profile, process_chunk
from .audio_visualizer import visualize_audio
from uuid import uuid4

# Load model
# for high accuracy
# processor = Wav2Vec2Processor.from_pretrained(
#     "facebook/wav2vec2-large-960h-lv60-self")
# model = Wav2Vec2ForCTC.from_pretrained(
#     "facebook/wav2vec2-large-960h-lv60-self")

# for fast processing
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")


def speech_to_text(chunk, sample_rate):
    """Processes an audio chunk through the ASR pipeline"""
    text = process_chunk(chunk, sample_rate, processor, model)
    print(f"Transcription ({len(text)} characters): {text}")
    return text


def split_audio_on_silence(audio_file):
    # Load audio file with fixed sample rate
    audio, sample_rate = librosa.load(
        audio_file, sr=16000, res_type='kaiser_best', mono=True
    )  # Forces 16kHz resampling
    print(f"Total duration: {len(audio)/sample_rate:.2f} seconds")

    # Extract noise profile from silent segments
    #noise_profile = find_noise_profile(audio, sample_rate)

    # Reduce noise in the audio chunk using the noise profile
    reduced_noise = nr.reduce_noise(
        y=audio,
        sr=sample_rate,
        prop_decrease=0.8,  # Proportion of noise to reduce
    )
    # Visualize the audio before and after noise reduction
    visualize_audio(audio, sample_rate,
                    f"{audio_file.split('.')[0]}_original.png")
    visualize_audio(reduced_noise, sample_rate,
                    f"{audio_file.split('.')[0]}_denoised.png")
    print("Noise reduction applied")
    # Save the denoised audio (optional)
    sf.write(
        f"{audio_file.split('.')[0]}_denoised.wav",
        reduced_noise,
        sample_rate
    )

    # Detect speech segments using energy threshold
    intervals = librosa.effects.split(
        audio,
        top_db=25,  # Silence threshold (higher = more sensitive)
        frame_length=2048,  # FFT window size
        hop_length=512,  # Analysis stride
    )
    print(f"Found {len(intervals)} speech segments")

    # Slice audio into chunks
    chunks = [audio[start:end] for start, end in intervals]

    return chunks, sample_rate
