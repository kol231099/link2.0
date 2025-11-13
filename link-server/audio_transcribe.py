# link-server/audio_transcribe.py
import os
import subprocess
from typing import Optional

from openai import OpenAI

# 這裡會自動吃環境變數 OPENAI_API_KEY（你已經在 main.py 用 dotenv 讀進來了）
client = OpenAI()


def extract_audio(video_path: str, out_dir: Optional[str] = None) -> str:
    """
    從 video_path 抽出音訊存成 mp3。
    - 成功：回傳 audio_path
    - 失敗：raise RuntimeError（讓 /ingest 知道是哪裡壞掉）
    """
    if out_dir is None:
        out_dir = os.path.dirname(video_path)

    os.makedirs(out_dir, exist_ok=True)
    audio_path = os.path.join(out_dir, "audio.mp3")

    cmd = [
        "ffmpeg",
        "-y",              # 覆蓋同名檔案
        "-i", video_path,  # 輸入影片
        "-vn",             # 不要影片，只要音訊
        "-acodec", "mp3",  # 轉成 mp3（你要別的格式也可以改）
        audio_path,
    ]

    print("🎧 ffmpeg cmd:", " ".join(cmd))
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        # ffmpeg 執行失敗，直接丟錯，把 stderr 帶出去方便 debug
        raise RuntimeError(f"ffmpeg failed (code={result.returncode}): {result.stderr}")

    if not os.path.exists(audio_path):
        # 理論上不應該發生，保險再檢查一次
        raise RuntimeError(f"audio file not created: {audio_path}")

    return audio_path


def transcribe_audio(audio_path: str) -> str:
    """
    把音訊丟給 OpenAI 做語音轉文字。
    假設 audio_path 一定存在，如果不存在視為後端邏輯錯誤。
    """
    if not os.path.exists(audio_path):
        raise RuntimeError(f"audio file missing before transcription: {audio_path}")

    with open(audio_path, "rb") as f:
        # 模型名稱你可以換成你有開通的，例如 "gpt-4o-mini-transcribe" 或 "whisper-1"
        resp = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=f,
            response_format="text",
        )
    # resp 已經是純文字（因為 response_format="text"）
    return resp


