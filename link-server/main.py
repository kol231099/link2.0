from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tempfile, subprocess, os

from ig_extract import extract_ig_metadata
from audio_transcribe import extract_audio, transcribe_audio
from video_ocr import ocr_video_frames
from html_parser import extract_html

app = FastAPI()

class IngestReq(BaseModel):
    url: str

@app.post("/ingest")
def ingest(req: IngestReq):
    url = req.url
    if not url.startswith("http"):
        raise HTTPException(400, "Invalid URL")

    print("📥 [Start] Ingest request received:", url)

    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = f"{tmpdir}/video.mp4"
        audio_path = f"{tmpdir}/audio.mp3"

        # Step 1: 下載影片（只為分析）
        print("🎬 [Step 1] 開始下載影片...")
        cookies = os.getenv("IG_COOKIES_FILE", "")
        cmd = ["yt-dlp", "-f", "mp4", "-o", video_path]
        if cookies and os.path.exists(cookies):
            print(f"🍪 使用 cookies 檔案: {cookies}")
            cmd += ["--cookies", cookies]
        cmd += [url]
        print("🧩 執行 yt-dlp 指令:", " ".join(cmd))
        subprocess.run(cmd, capture_output=True)
        print("✅ [Step 1] 影片下載完成")

        # Step 2: 音訊逐字稿
        print("🎧 [Step 2] 開始抽取音訊與轉文字...")
        extract_audio(video_path, audio_path)
        print("🔊 音訊擷取完成:", audio_path)
        transcript = transcribe_audio(audio_path)
        print("📝 Whisper 轉文字完成，文字長度:", len(transcript))

        # Step 3: OCR
        print("🔍 [Step 3] 開始影像 OCR 分析...")
        ocr_texts = ocr_video_frames(video_path)
        print("✅ [Step 3] OCR 完成，偵測文字數量:", len(ocr_texts))

        # Step 4: HTML 解析
        print("🌐 [Step 4] 開始解析 HTML...")
        desc_html = extract_html(url)
        print("✅ [Step 4] HTML 解析完成")

    print("🏁 [Done] 全部流程完成 ✅")

    return {
        "status": "ready",
        "transcript": transcript[:500],  # 太長可截斷
        "ocr_text": ocr_texts,
        "html_description": desc_html
    }


