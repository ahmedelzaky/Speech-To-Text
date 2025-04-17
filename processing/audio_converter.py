import ffmpeg


def convert_to_wav(input_path: str, output_path: str, sample_rate=16000) -> bool:
    """Convert audio file to WAV format with specified sample rate and make it mono"""
    try:
        ffmpeg.input(input_path).output(
            output_path, ar=sample_rate, ac=1).run(overwrite_output=True)
        return True
    except ffmpeg.Error as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return False
