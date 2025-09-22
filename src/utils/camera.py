import cv2
import asyncio
from typing import Optional

async def open_camera() -> Optional[cv2.VideoCapture]:
    BACKENDS = [
        cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_VFW,
        cv2.CAP_GSTREAMER, cv2.CAP_FFMPEG, cv2.CAP_OPENCV_MJPEG
    ]
    for idx in range(0, 8):
        for be in BACKENDS:
            cap = cv2.VideoCapture(idx, be)
            if not cap.isOpened():
                cap.release()
                continue
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            for _ in range(5):
                cap.read()
                await asyncio.sleep(0.05)
            ok, frame = cap.read()
            if ok and frame is not None:
                print(f"✅ 카메라 {idx} / {be} 열기 성공, frame={frame.shape}")
                return cap
            cap.release()
    print("❌ 사용 가능한 카메라 없음")
    return None
