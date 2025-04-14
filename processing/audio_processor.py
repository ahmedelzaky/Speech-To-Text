import noisereduce as nr
import librosa
import torch 
# reduce noise in audio and chunk
def find_noise_profile(audio, sample_rate):
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
