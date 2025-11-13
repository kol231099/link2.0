# video_ocr.py
import time
from functools import lru_cache
from paddleocr import PaddleOCR

@lru_cache(maxsize=1)
def get_ocr():
    t0 = time.time()
    print("📦 [OCR] Loading PaddleOCR models (lang=ch)...")
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)  # 只關閉冗長 log
    print(f"📦 [OCR] Models ready in {time.time()-t0:.1f}s")
    return ocr

def ocr_video_frames(video_path: str, sample_fps: float = 0.25, max_frames: int = 10):
    print(f"🖼  [OCR] 開始處理影片：{video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ [OCR] 無法開啟影片")
        return []

    native_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    step = max(int(native_fps / sample_fps), 1)
    print(f"🧮 [OCR] 影片FPS={native_fps:.2f}, 總影格={total_frames}, 取樣步長={step}, 上限={max_frames}")

    # 這行是最可能卡住的點：第一次下載/載入模型
    t0 = time.time()
    ocr = get_ocr()
    print(f"⏱️ [OCR] get_ocr() spent {time.time()-t0:.1f}s")

    results, taken, frame_idx = [], 0, 0
    while frame_idx < total_frames and taken < max_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        if not ok:
            break

        # 第一次推論也可能較慢
        t1 = time.time()
        ocr_out = ocr.ocr(frame)
        print(f"⏱️ [OCR] one frame infer {time.time()-t1:.2f}s (#{taken+1})")

        texts = []
        for line in (ocr_out or []):
            for box, (txt, conf) in line:
                if txt:
                    texts.append(txt)
        results.append(" ".join(texts).strip())

        taken += 1
        print(f"⏳ [OCR] 已處理 {taken}/{max_frames} 張…")
        frame_idx += step

    cap.release()
    print(f"✅ [OCR] 完成，共 {len(results)} 張影格")
    return results
