import librosa
import torch

# Function to find a noise profile from silent segments in the audio
# This helps in identifying what background noise to remove


def find_noise_profile(audio, sample_rate):
    """
    Identify silent segments in audio to extract noise profile.

    Args:
        audio (np.array): Audio signal as numpy array
        sample_rate (int): Sample rate of the audio

    Returns:
        np.array: Segment of audio containing just noise (for noise reduction)
    """
    # Split audio into segments where sound is detected (non-silent intervals)
    intervals = librosa.effects.split(
        audio, top_db=20, frame_length=1024, hop_length=512)

    # If silent segments found, use first segment as noise profile
    if len(intervals) > 0:
        return audio[intervals[0][0]:intervals[0][1]]

    # If no silent segments found, return first second of audio as fallback
    return audio[:sample_rate]

# Function to process an audio chunk through noise reduction and speech recognition


def process_chunk(chunk, sample_rate, processor, model):
    """
    Process an audio chunk through noise reduction and speech recognition.

    Args:
        chunk (np.array): Audio chunk to process
        sample_rate (int): Sample rate of the audio
        processor: HuggingFace processor for the ASR model
        model: HuggingFace ASR model

    Returns:
        str: Recognized text from the audio chunk
    """
    # Prepare audio for the ASR model using the processor
    inputs = processor(
        chunk,
        sampling_rate=sample_rate,
        return_tensors="pt",  # Return PyTorch tensors
        padding=True
    )

    # Run inference (with gradient calculation disabled for efficiency)
    with torch.no_grad():
        logits = model(inputs.input_values).logits

    # Decode the predicted tokens into text
    predicted_ids = torch.argmax(logits, dim=-1)
    return processor.batch_decode(predicted_ids)[0]
