import os, subprocess, json, re

def extract_html(url: str) -> str:
    cookies = os.getenv("IG_COOKIES_FILE", "")
    cmd = ["yt-dlp", "--dump-json", "--no-playlist", "--skip-download"]
    if cookies and os.path.exists(cookies):
        cmd += ["--cookies", cookies]
    cmd += [url]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(p.stdout)
        html_desc = data.get("description", "")
        return html_desc
    except Exception as e:
        print("HTML parse fail:", e)
        return ""
