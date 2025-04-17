from fastapi import FastAPI, WebSocketDisconnect, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from processing.audio_converter import convert_to_wav
from processing.speech_recognizer import speech_to_text, split_audio_on_silence
import yt_dlp
from concurrent.futures import ThreadPoolExecutor
import asyncio
import tempfile
import re
from uuid import uuid4
import os

app = FastAPI()
YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'


origins = [
    "http://localhost:8080",
    "http://localhost:4173",
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


@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Step 1: receive metadata (e.g., {"filename": "recording.mp3"})
            file_info = await websocket.receive_json()
            original_filename = file_info.get("filename", "audio.unknown")

            # Step 2: receive binary audio file
            audio_bytes = await websocket.receive_bytes()

            # Prepare paths
            _, ext = os.path.splitext(original_filename)
            temp_dir = tempfile.gettempdir()
            input_path = os.path.join(temp_dir, f"{uuid4().hex}{ext}")
            wav_path = input_path  # Default

            # Save original file
            with open(input_path, "wb") as f:
                f.write(audio_bytes)

            # Convert if not WAV
            if ext.lower() != ".wav":
                wav_path = os.path.join(temp_dir, f"{uuid4().hex}.wav")
                if not convert_to_wav(input_path, wav_path):
                    await websocket.send_json({"error": "Conversion to WAV failed"})
                    os.remove(input_path)
                    continue

            # Transcribe and stream results
            async for text_chunk in process_audio_chunks(wav_path):
                await websocket.send_json({"text": text_chunk})

            await websocket.send_json({"status": "complete"})

            # Clean up
            for path in {input_path, wav_path}:
                if os.path.exists(path):
                    os.remove(path)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})


@app.websocket("/ws/transcribe-youtube")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    executor = ThreadPoolExecutor()

    try:
        # Receive YouTube URL from client
        data = await websocket.receive_json()
        url = data.get('url')

        if not url:
            await websocket.send_json({"error": "Missing YouTube URL"})
            return

        # Send initial status
        await websocket.send_json({"status": "downloading"})

        # Download audio
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
            'progress_hooks': [lambda d: print(f"Download progress: {d.get('_percent_str', 'N/A')}")]
        }

        # Run blocking tasks in thread pool
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(executor, download_audio, url, ydl_opts)

        # Send conversion status
        await websocket.send_json({"status": "converting"})

        # Process audio in chunks
        async for text_chunk in process_audio_chunks(info['filename']):
            await websocket.send_json({"text": text_chunk})

        await websocket.send_json({"status": "complete"})

    except Exception as e:
        await websocket.send_json({"error": str(e)})
        print(f"Error: {e}")
    finally:
        await websocket.close()


def download_audio(url: str, ydl_opts: dict):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        # Construct filename from output template
        filename = ydl.prepare_filename(info)
        # Replace extension with .wav if postprocessing converts it
        filename = filename.rsplit(".", 1)[0] + ".wav"

        info['filename'] = filename
        return info


async def process_audio_chunks(filename: str):
    chunks,  sample_rate, noise_profile = split_audio_on_silence(filename)
    for chunk in chunks:
        yield speech_to_text(chunk, sample_rate, noise_profile)
