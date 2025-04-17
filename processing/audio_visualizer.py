import matplotlib.pyplot as plt
import librosa.display
import matplotlib
import numpy as np

# Set non-GUI backend for matplotlib (critical for server environments)
matplotlib.use('Agg')  # Prevents trying to connect to display


def visualize_audio(audio, sample_rate, output_path="audio.png"):
    """
    Generate professional audio visualization with waveform and spectrogram.

    Optimized for:
    - Reduced memory usage
    - Faster spectrogram computation
    - Clean visual presentation

    Args:
        audio (np.ndarray): Input audio signal (1D array)
        sample_rate (int): Sampling rate in Hz
        output_path (str): Output file path (default: "audio.png")

    Returns:
        None (saves plot to file)
    """
    # Create figure with constrained layout to prevent label clipping
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8),
                                   constrained_layout=True)

    # 1. Waveform Plot (Top Panel)
    librosa.display.waveshow(audio, sr=sample_rate, ax=ax1, color='#1f77b4')
    ax1.set_title("Waveform (Time Domain)", fontsize=12, pad=10)
    ax1.set_xlabel("")
    ax1.grid(True, alpha=0.3)

    # 2. Spectrogram Plot (Bottom Panel)
    # Optimized STFT computation with sensible defaults
    stft = librosa.stft(audio, n_fft=2048, hop_length=512, win_length=1024)
    spectrogram = librosa.amplitude_to_db(np.abs(stft), ref=np.max)

    # Custom colormap that's perceptually uniform
    img = librosa.display.specshow(spectrogram, sr=sample_rate,
                                   x_axis='time', y_axis='log',
                                   ax=ax2, cmap='magma',
                                   hop_length=512)

    ax2.set_title("Spectrogram (Frequency Domain)", fontsize=12, pad=10)
    fig.colorbar(img, ax=ax2, format="%+2.0f dB", pad=0.02)

    # Save with optimized settings
    plt.savefig(output_path,
                dpi=100,  # Reduced from default 300 for smaller files
                bbox_inches='tight',
                pad_inches=0.2,
                facecolor='black')

    # Explicit cleanup
    plt.close(fig)
    del fig, stft, spectrogram  # Free memory
