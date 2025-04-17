import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from .audio_processor import find_noise_profile, process_chunk
from .audio_visualizer import visualize_audio

# Load model
processor = Wav2Vec2Processor.from_pretrained(
    "facebook/wav2vec2-base-960h")  # Handles audio feature extraction
model = Wav2Vec2ForCTC.from_pretrained(
    "facebook/wav2vec2-base-960h")  # ASR model


def speech_to_text(chunk, sample_rate, noise_profile):
    """Processes an audio chunk through the ASR pipeline"""
    text = process_chunk(chunk, sample_rate, processor, model, noise_profile)
    print(f"Transcription ({len(text)} characters): {text}")
    return text


def split_audio_on_silence(audio_file):
    # Load audio file with fixed sample rate
    audio, sample_rate = librosa.load(
        audio_file, sr=16000, res_type='kaiser_best', mono=True
    )  # Forces 16kHz resampling
    print(f"Total duration: {len(audio)/sample_rate:.2f} seconds")

    # Generate visualization (debugging aid)
    visualize_audio(audio, sample_rate, audio_file.replace(".wav", ".png"))

    # Extract noise profile from silent segments
    noise_profile = find_noise_profile(audio, sample_rate)

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

    return chunks, sample_rate, noise_profile
