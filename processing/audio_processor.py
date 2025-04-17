import noisereduce as nr
import librosa
import torch


def find_noise_profile(audio, sample_rate, min_duration=0.5):
    """
    Extracts a noise profile from a quiet section of the audio.
    This is used as a reference for noise reduction later.

    Parameters:
        audio (np.ndarray): The audio waveform (time series data)
        sample_rate (int): Samples per second (Hz)
        min_duration (float): Minimum length of noise sample to extract (in seconds)

    Returns:
        np.ndarray: A sample of background noise to use as reference

    Note:
        - Uses librosa's voice activity detection to find silent intervals
        - Falls back to first 'min_duration' seconds if no silence is found
        - The quality of noise reduction heavily depends on this profile
    """
    min_samples = int(min_duration * sample_rate)

    # Detect non-silent intervals (voice/sound regions)
    intervals = librosa.effects.split(
        audio,
        top_db=25,  # Threshold for silence detection (higher = more sensitive)
        frame_length=1024,  # FFT window size
        hop_length=256  # Distance between frames
    )

    # If no voice activity detected, use beginning of audio
    if len(intervals) == 0:
        return audio[:min_samples]

    # Vectorized slice calculation
    start = max(0, intervals[0][0] - min_samples)
    return audio[start:intervals[0][0]] if start < intervals[0][0] else audio[:min_samples]


def process_chunk(chunk, sample_rate, processor, model, noise_profile):
    """
    Processes an audio chunk through noise reduction and speech recognition.

    Parameters:
        chunk (np.ndarray): Audio segment to process
        sample_rate (int): Audio sample rate
        processor: HuggingFace Whisper feature extractor
        model: Pretrained Whisper ASR model
        noise_profile (np.ndarray): Reference noise sample

    Returns:
        str: Recognized text from the audio chunk

    Processing Pipeline:
        1. Noise reduction using the reference profile
        2. Audio feature extraction
        3. Speech recognition inference
        4. Text decoding
    """
    # Step 1: Reduce background noise
    reduced_noise = nr.reduce_noise(
        y=chunk,
        y_noise=noise_profile,  # Reference noise from find_noise_profile()
        sr=sample_rate,
        prop_decrease=0.85,  # Aggressiveness of noise reduction (0-1)
        n_fft=512,  # Smaller FFT window
        win_length=400  # Optimized window length
    )

    # Step 2: Prepare features for Whisper model
    inputs = processor(
        reduced_noise,
        sampling_rate=sample_rate,
        return_tensors="pt",   # PyTorch tensors
        padding=True,  # Pad to max length in batch
    )

    # Step 3: Run inference (no gradients for efficiency)
    with torch.no_grad():
        logits = model(inputs.input_values).logits

    # Step 4: Decode predicted tokens to text
    predicted_ids = torch.argmax(logits, dim=-1)
    return processor.batch_decode(predicted_ids)[0]
