from pathlib import Path
from dotenv import load_dotenv

# 讀取跟 main.py 同一個資料夾的 .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tempfile, subprocess, os, sys

from ig_extract import extract_ig_metadata
from audio_transcribe import extract_audio, transcribe_audio
from video_ocr import ocr_video_frames
from html_parser import extract_html


app = FastAPI()


class IngestReq(BaseModel):
    url: str


@app.post("/ingest")
def ingest(req: IngestReq):
    url = req.url.strip()
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL")

    print("📥 [Start] Ingest request received:", url)

    try:
        # 用同一個 TemporaryDirectory 放影片和音訊
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = f"{tmpdir}/video.mp4"

            # ------------------------
            # Step 0: (可選) 抓 IG metadata
            # ------------------------
            try:
                meta = extract_ig_metadata(url)
            except Exception as e:
                print("⚠️ extract_ig_metadata 失敗，略過:", repr(e))
                meta = None

            # ------------------------
            # Step 1: 下載影片（yt-dlp）
            # ------------------------
            print("🎬 [Step 1] 開始下載影片...")
            cookies = os.getenv("IG_COOKIES_FILE", "")

            # 用目前這個 venv 的 Python 來跑 yt_dlp
            cmd = [
                sys.executable,
                "-m", "yt_dlp",
                "-f", "mp4",
                "-o", video_path,
                url,
            ]

            if cookies and os.path.exists(cookies):
                print(f"🍪 使用 cookies 檔案: {cookies}")
                cmd += ["--cookies", cookies]

            print("🧩 執行 yt-dlp 指令:", " ".join(cmd))
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"yt-dlp failed (code={result.returncode}): {result.stderr}"
                )

            print("✅ [Step 1] 影片下載完成:", video_path)

            # ------------------------
            # Step 2: 抽音訊（ffmpeg）
            # ------------------------
            print("🎧 [Step 2] 開始抽取音訊...")
            # 這裡預期 audio_transcribe.extract_audio 定義為：
            #   def extract_audio(video_path: str, out_dir: str) -> str
            audio_path = extract_audio(video_path, tmpdir)
            print("🔊 音訊擷取完成:", audio_path)

            # ------------------------
            # Step 3: 語音轉文字（OpenAI）
            # ------------------------
            print("📝 [Step 3] 開始語音轉文字（STT）...")
            transcript = transcribe_audio(audio_path)
            print("📝 Whisper 轉文字完成，文字長度:", len(transcript))

            # ------------------------
            # Step 4: OCR
            # ------------------------
            print("🔍 [Step 4] 開始影像 OCR 分析...")
            ocr_texts = ocr_video_frames(video_path)
            print("✅ [Step 4] OCR 完成，偵測文字數量:", len(ocr_texts))

            # ------------------------
            # Step 5: HTML 解析
            # ------------------------
            print("🌐 [Step 5] 開始解析 HTML...")
            desc_html = extract_html(url)
            print("✅ [Step 5] HTML 解析完成")

            print("🏁 [Done] 全部流程完成 ✅")

            return {
                "status": "ready",
                "transcript": transcript[:500],  # 太長就截 500 字
                "ocr_text": ocr_texts,
                "html_description": desc_html,
                "metadata": meta,
            }

    except RuntimeError as e:
        # 我們自己在 yt-dlp / ffmpeg / transcribe_audio 裡 raise 的錯
        print("❌ [RuntimeError]:", e)
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        # 其他未預期錯誤
        print("💥 [Unexpected Error]:", repr(e))
        raise HTTPException(status_code=500, detail="Internal server error")



