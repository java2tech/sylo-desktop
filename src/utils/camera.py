import cv2
import asyncio
from typing import Optional, Tuple

async def _read_with_timeout(cap: cv2.VideoCapture, timeout: float) -> Tuple[bool, Optional[any]]:
    try:
        return await asyncio.wait_for(asyncio.to_thread(cap.read), timeout)
    except asyncio.TimeoutError:
        return False, None

async def open_camera() -> Optional[cv2.VideoCapture]:
    BACKENDS = [
        cv2.CAP_DSHOW,
        cv2.CAP_FFMPEG,
        cv2.CAP_ANY,
        cv2.CAP_VFW,
        cv2.CAP_GSTREAMER,
        cv2.CAP_MSMF,
    ]
    for idx in range(0, 4):
        for be in BACKENDS:
            cap = cv2.VideoCapture(idx, be)
            if not cap.isOpened():
                cap.release()
                continue
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            for _ in range(20):
                ok, _ = await _read_with_timeout(cap, 3.5)
                if not ok:
                    break
                await asyncio.sleep(0.05)
            ok, frame = await _read_with_timeout(cap, 3.5)
            if ok and frame is not None:
                print(f"✅ 카메라 {idx} / {be} 열기 성공, frame={frame.shape}")
                return cap
            cap.release()
    print("❌ 사용 가능한 카메라 없음")
    return None
