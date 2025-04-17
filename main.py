from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from processing.audio_converter import convert_to_wav
from processing.speech_recognizer import speech_to_text
import yt_dlp
import uuid
from typing import Optional
import re
import os

app = FastAPI()
YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'


origins = [
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Create a temporary directory
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)

        # Save uploaded file directly with original extension
        input_path = os.path.join(temp_dir, file.filename)
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Convert to WAV
        if file.filename.lower().endswith(('.wav')):
            wav_path = input_path
        else:
            wav_path = os.path.join(
                temp_dir, f"{os.path.splitext(file.filename)[0]}.wav")
            if not convert_to_wav(input_path, wav_path):
                raise HTTPException(
                    status_code=400, detail="Conversion failed")

        # Transcribe
        text = speech_to_text(wav_path)

        # Cleanup
        for path in [input_path, wav_path]:
            if os.path.exists(path):
                os.remove(path)

        return {"transcription": text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe-youtube")
async def transcribe_youtube(
    url: str = Body(..., embed=True,
                    example="https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
    max_duration: Optional[int] = Body(3600)  # Default 1 hour limit
):
    try:
        # Validate YouTube URL
        if not re.match(YOUTUBE_REGEX, url, re.IGNORECASE):
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_uploads/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'max_duration': max_duration,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_filename = ydl.prepare_filename(info).replace(
                '.webm', '.wav').replace('.m4a', '.wav')

            if not os.path.exists(audio_filename):
                raise HTTPException(
                    status_code=500, detail="Failed to download audio")

            # Transcribe using existing function
            text = speech_to_text(audio_filename)

            # Cleanup
            os.remove(audio_filename)

            return {"transcription": text}

    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(
            status_code=400, detail=f"YouTube download failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
