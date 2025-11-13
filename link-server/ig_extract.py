# ig_extract.py
import os, json, subprocess, tempfile, pathlib

def _cookies_arg():
    p = os.getenv("IG_COOKIES_FILE", "").strip()
    return ["--cookies", p] if p and os.path.exists(p) else []

def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True)

def extract_ig_metadata(url: str) -> dict:
    """
    取得 IG 影片的基本資訊（含說明欄），不下載影片。
    回傳: {"id","title","uploader","duration","description"}
    """
    cmd = ["yt-dlp", "--dump-json", "--no-warnings", "--skip-download"]
    cmd += _cookies_arg()
    cmd += [url]
    p = _run(cmd)
    if p.returncode != 0 or not p.stdout.strip():
        raise RuntimeError(f"yt-dlp metadata failed: {p.stderr.strip()}")
    data = json.loads(p.stdout)
    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "uploader": data.get("uploader"),
        "duration": data.get("duration"),
        "description": data.get("description") or "",
    }

def download_ig_video(url: str, out_path: str) -> str:
    """
    下載 IG 影片到 out_path（如 /tmp/video.mp4）。
    回傳實際下載後的檔案路徑（含副檔名）。
    """
    out_path = str(pathlib.Path(out_path))
    # 指定容器格式 mp4；若取不到 mp4，yt-dlp 會轉擋或選擇最接近格式
    cmd = ["yt-dlp", "-f", "mp4", "-o", out_path]
    cmd += _cookies_arg()
    cmd += [url]
    p = _run(cmd)
    if p.returncode != 0:
        raise RuntimeError(f"yt-dlp download failed: {p.stderr.strip()}")

    # 如果 -o 指的是不含副檔名的固定名稱，yt-dlp 可能會自動加 .mp4；統一找出實際檔名
    base = out_path
    if os.path.exists(base):
        return base
    if os.path.exists(base + ".mp4"):
        return base + ".mp4"

    # 或者 yt-dlp 可能用到模板，補個保險：取同資料夾最新的 mp4
    folder = str(pathlib.Path(out_path).parent)
    mp4s = sorted(
        [str(pathlib.Path(folder, f)) for f in os.listdir(folder) if f.endswith(".mp4")],
        key=lambda pth: os.path.getmtime(pth),
        reverse=True,
    )
    if mp4s:
        return mp4s[0]

    raise FileNotFoundError("Video file not found after yt-dlp download")
