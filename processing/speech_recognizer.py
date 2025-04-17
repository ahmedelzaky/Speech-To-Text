import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from .audio_processor import find_noise_profile, process_chunk
from .audio_visualizer import visualize_audio

# Load model
processor = Wav2Vec2Processor.from_pretrained(
    "facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")


def speech_to_text(chunk, sample_rate, noise_profile):
    text = process_chunk(chunk, sample_rate, processor, model, noise_profile)
    print(f"Transcription ({len(text)} characters): {text}")
    return text


def split_audio_on_silence(audio_file):
    # Load audio file
    audio, sample_rate = librosa.load(audio_file, sr=16000)
    print(f"Total duration: {len(audio)/sample_rate:.2f} seconds")

    visualize_audio(audio, sample_rate, audio_file.replace(".wav", ".png"))

    # Generate noise profile
    noise_profile = find_noise_profile(audio, sample_rate)

    # Get intervals of speech (not silence)
    intervals = librosa.effects.split(
        audio, top_db=25, frame_length=2048, hop_length=512)

    print(f"Found {len(intervals)} speech segments")

    # Extract audio segments
    chunks = [audio[start:end] for start, end in intervals]

    return chunks, sample_rate, noise_profile
