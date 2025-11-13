# audio_transcribe.py
import os, subprocess, tempfile
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 確保匯入時就抓到 .env

def extract_audio(video_path: str, audio_path: str) -> str:
    """用 ffmpeg 從影片擷取音訊"""
    cmd = ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "mp3", audio_path]
    subprocess.run(cmd, capture_output=True)

def transcribe_audio(audio_path: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    if not client.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    with open(audio_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return resp.text

