# Audio Transcription Service

A real-time audio transcription service that supports file uploads, YouTube URLs, and live recordings. Built with FastAPI backend and React frontend.

## Features

- 🎙️ **Multiple input sources**:
  - Upload audio files (MP3, WAV, etc.)
  - Input YouTube URLs
  - Live microphone recording
- ⚡ **Real-time transcription** streaming via WebSockets
- 🔊 **Automatic audio conversion** using FFmpeg
- 🔇 **Noise reduction** and silence detection
- 🌐 **CORS support** for cross-origin requests
- 📦 **Container-ready** architecture

## Technologies

### Backend
- Python 3.9+ with FastAPI
- WebSockets for real-time communication
- yt-dlp for YouTube audio extraction
- FFmpeg for audio processing

### Frontend
- React with TypeScript
- Web Audio API
- Tailwind CSS
- WebSocket client integration

## Installation

### Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install

# Start development server
npm run dev
```

## Project Structure

```
audio-transcription-service/
├── backend/
│   ├── main.py            # FastAPI app entrypoint
│   ├── processing/        # Audio processing modules
│   └── requirements.txt   # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/    # React components
    │   ├── App.tsx        # Main application
    │   └── main.tsx       # Entry point
    └── index.html         # Base HTML template
```


## Usage

1. Access the web interface at `http://localhost:8080`
2. Choose input method:
   - **File Upload**: Drag & drop or select audio file
   - **YouTube URL**: Paste any YouTube video URL
   - **Live Recording**: Click microphone icon
3. View real-time transcription results

## Troubleshooting

**Common Issues**:

1. **FFmpeg not found**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   ```

2. **WebSocket connection errors**:
   - Verify backend service is running
   - Check CORS settings in `main.py`
