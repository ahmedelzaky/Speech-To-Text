# First update librosa in your environment:
# pip install --upgrade librosa

import librosa
import numpy as np
import matplotlib.pyplot as plt
import noisereduce as nr
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import ffmpeg
import os

def convert_to_wav(input_path: str, output_path: str):
    try:
        ffmpeg.input(input_path).output(
            output_path, ar=16000).run(overwrite_output=True)
        return True
    except ffmpeg.Error as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return False

def visualize_audio(audio, sample_rate):
    plt.figure(figsize=(12, 8))
    
    # Plot waveform
    plt.subplot(2, 1, 1)
    librosa.display.waveshow(audio, sr=sample_rate)
    plt.title("Waveform (Amplitude over Time)")
    
    # Plot spectrogram with magnitude calculation
    plt.subplot(2, 1, 2)
    stft = librosa.stft(audio)
    spectrogram = np.abs(stft)  # Take absolute value for magnitude
    librosa.display.specshow(librosa.amplitude_to_db(spectrogram, ref=np.max),
                             sr=sample_rate, x_axis="time", y_axis="log")
    plt.title("Spectrogram (Frequency over Time)")
    plt.colorbar(format="%+2.0f dB")
    plt.tight_layout()
    plt.savefig("audio.png")

def find_noise_profile(audio, sample_rate):
    # Use librosa's voice detection to find noise segments
    intervals = librosa.effects.split(audio, top_db=20, frame_length=2048, hop_length=512)
    if len(intervals) > 0:
        return audio[intervals[0][0]:intervals[0][1]]
    return audio[:sample_rate]

def process_chunk(chunk, sample_rate, processor, model, noise_profile):
    reduced_noise = nr.reduce_noise(
        y=chunk,
        y_noise=noise_profile,
        sr=sample_rate,
        prop_decrease=0.9
    )

    inputs = processor(
        reduced_noise,
        sampling_rate=sample_rate,
        return_tensors="pt",
        padding=True
    )

    with torch.no_grad():
        logits = model(inputs.input_values).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    return processor.batch_decode(predicted_ids)[0]

def speech_to_text(audio_file):
    audio, sample_rate = librosa.load(audio_file, sr=16000)
    print(f"Total duration: {len(audio)/sample_rate:.2f} seconds")

    visualize_audio(audio, sample_rate)

    # Find noise profile
    noise_profile = find_noise_profile(audio, sample_rate)

    # Split on silence using updated librosa
    chunks = librosa.effects.split(audio, top_db=25, frame_length=2048, hop_length=512)
    print(f"Found {len(chunks)} speech segments")

    # Load model
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

    full_text = []
    for i, (start, end) in enumerate(chunks):
        chunk = audio[start:end]
        print(f"Processing segment {i+1}/{len(chunks)} ({len(chunk)/sample_rate:.2f}s)")
        text = process_chunk(chunk, sample_rate, processor, model, noise_profile)
        print(f"Transcription ({len(text)} characters): {text}")
        full_text.append(text)
    
    return " ".join(full_text)

if __name__ == "__main__":
    audio_file_path = "test.mp3"
    wav_file_path = "audio.wav"

    if convert_to_wav(audio_file_path, wav_file_path):
        print("Conversion successful")
        result = speech_to_text(wav_file_path)
        print("\nFinal Transcription:")
        print(result)
    else:
        print("Conversion failed")