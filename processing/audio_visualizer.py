import librosa.display
import matplotlib.pyplot as plt
import numpy as np

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
