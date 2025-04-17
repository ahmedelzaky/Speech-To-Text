import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from .audio_processor import find_noise_profile, process_chunk
from .audio_visualizer import visualize_audio

# Load model
processor = Wav2Vec2Processor.from_pretrained(
    "facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")


def speech_to_text(audio_file):
    audio, sample_rate = librosa.load(audio_file, sr=16000)
    print(f"Total duration: {len(audio)/sample_rate:.2f} seconds")

    visualize_audio(audio, sample_rate, audio_file.replace(".wav", ".png"))

    # Find noise profile
    noise_profile = find_noise_profile(audio, sample_rate)

    # Split on silence using updated librosa
    chunks = librosa.effects.split(
        audio, top_db=25, frame_length=2048, hop_length=512)
    print(f"Found {len(chunks)} speech segments")

    full_text = []
    for i, (start, end) in enumerate(chunks):
        chunk = audio[start:end]
        print(
            f"Processing segment {i+1}/{len(chunks)} ({len(chunk)/sample_rate:.2f}s)")
        text = process_chunk(chunk, sample_rate,
                             processor, model, noise_profile)
        print(f"Transcription ({len(text)} characters): {text}")
        full_text.append(text)

    return " ".join(full_text)
