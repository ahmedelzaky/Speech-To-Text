from fastapi import FastAPI, UploadFile, File, HTTPException
from processing import convert_to_wav, speech_to_text
import shutil
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    input_path = f"temp_{file.filename}" # Temporary file path 

    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert to WAV
    wav_path = "audio.wav"
    if not convert_to_wav(input_path, wav_path):
        return {"error": "Conversion failed"}

    # Transcribe
    text = speech_to_text(wav_path)

    # Cleanup
    os.remove(input_path)
    os.remove(wav_path)

    return {"transcription": text}

