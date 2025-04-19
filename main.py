from fastapi import FastAPI, WebSocketDisconnect, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from processing.audio_converter import convert_to_wav
from processing.speech_recognizer import speech_to_text, split_audio_on_silence
import yt_dlp
from concurrent.futures import ThreadPoolExecutor
import asyncio
import tempfile
from uuid import uuid4
import os

# Initialize FastAPI application
app = FastAPI()

# Regular expression to validate YouTube URLs
YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows frontend applications from these origins to access the API
origins = [
    "http://localhost:8080",  # Common Vue.js dev server port
    "http://localhost:4173",  # Common Vite preview port
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allowed origins
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],     # Allow all methods
    allow_headers=["*"],     # Allow all headers
)


@app.get("/")
def read_root():
    """Basic health check endpoint"""
    return {"Hello": "World"}


@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for audio file transcription.

    Handles both the upload and real-time transcription of audio files.
    Workflow:
    1. Receives metadata (filename) as JSON
    2. Receives audio binary data
    3. Converts to WAV if needed
    4. Processes audio in chunks
    5. Streams transcription results back
    6. Cleans up temporary files
    """
    await websocket.accept()
    try:
        # Step 1: Receive metadata (e.g., {"filename": "recording.mp3"})
        file_info = await websocket.receive_json()
        original_filename = file_info.get("filename", "audio.unknown")

        # Step 2: Receive binary audio file
        audio_bytes = await websocket.receive_bytes()

        # Prepare temporary file paths
        _, ext = os.path.splitext(original_filename)
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)  # Ensure temp directory exists
        input_path = os.path.join(temp_dir, f"{uuid4().hex}{ext}")
        wav_path = input_path  # Default path if no conversion needed

        # Save original file to temporary location
        with open(input_path, "wb") as f:
            f.write(audio_bytes)

        # Convert to WAV if not already in WAV format
        if ext.lower() != ".wav":
            wav_path = os.path.join(temp_dir, f"{uuid4().hex}.wav")
            if not convert_to_wav(input_path, wav_path):
                await websocket.send_json({"error": "Conversion to WAV failed"})
                os.remove(input_path)

        # Process audio in chunks and stream transcription results
        async for text_chunk in process_audio_chunks(wav_path):
            await websocket.send_json({"text": text_chunk})

        # Signal completion
        await websocket.send_json({"status": "complete"})

        # Clean up temporary files
        for path in {input_path, wav_path}:
            if os.path.exists(path):
                os.remove(path)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})


@app.websocket("/ws/transcribe-youtube")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for YouTube video transcription.

    Workflow:
    1. Receives YouTube URL
    2. Downloads audio using yt-dlp
    3. Converts to WAV
    4. Processes audio in chunks
    5. Streams transcription results back
    """
    await websocket.accept()
    executor = ThreadPoolExecutor()  # For running blocking IO operations

    try:
        # Receive YouTube URL from client
        data = await websocket.receive_json()
        url = data.get('url')

        if not url:
            await websocket.send_json({"error": "Missing YouTube URL"})
            return

        # Send initial status to client
        await websocket.send_json({"status": "downloading"})

        # YouTube download configuration
        ydl_opts = {
            'format': 'bestaudio/best',  # Get best quality audio
            'outtmpl': 'temp_uploads/%(id)s.%(ext)s',  # Output template
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',  # Convert to WAV format
                'preferredquality': '192',  # Audio quality
            }],
            'noplaylist': True,  # Don't download playlists
            'no_warnings': True,  # Suppress warnings
            # send progress % updates to client
            'progress_hooks': [lambda d: asyncio.run(websocket.send_json({"progress": d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100}))]
        }

        # Run blocking download in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(executor, download_audio, url, ydl_opts)

        # Notify client that conversion is starting
        await websocket.send_json({"status": "converting"})

        # Process audio and stream transcription chunks
        async for text_chunk in process_audio_chunks(info['filename']):
            await websocket.send_json({"text": text_chunk})

        # Signal completion
        await websocket.send_json({"status": "complete"})

    except Exception as e:
        await websocket.send_json({"error": str(e)})
        print(f"Error: {e}")
    finally:
        await websocket.close()


def download_audio(url: str, ydl_opts: dict):
    """
    Downloads audio from YouTube using yt-dlp.

    Args:
        url: YouTube URL to download
        ydl_opts: YouTube download options

    Returns:
        dict: Video info with added 'filename' pointing to downloaded WAV file
    """
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        # Construct filename from output template
        filename = ydl.prepare_filename(info)
        # Replace extension with .wav (postprocessor converts to WAV)
        filename = filename.rsplit(".", 1)[0] + ".wav"

        info['filename'] = filename
        return info


async def process_audio_chunks(filename: str):
    """
    Processes audio file in chunks and yields transcribed text.

    Args:
        filename: Path to WAV audio file

    Yields:
        str: Chunks of transcribed text
    """
    # Split audio into chunks based on silence
    chunks, sample_rate, noise_profile = split_audio_on_silence(filename)

    # Process each chunk and yield transcription
    for chunk in chunks:
        yield speech_to_text(chunk, sample_rate, noise_profile)
