from fastapi import FastAPI, UploadFile, File
from processing import convert_to_wav, speech_to_text  # Note the dotimport shutil
import os
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save uploaded file
    input_path = file.filename
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert to WAV
    wav_path = "audio.wav"
    if not convert_to_wav(input_path, wav_path):
        return {"error": "Conversion failed"}

    # Transcribe
    text = speech_to_text(wav_path)

    # Optional: cleanup
    os.remove(input_path)
    os.remove(wav_path)

    return {"transcription": text}