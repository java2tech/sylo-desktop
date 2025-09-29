# utils/camerav2.py

import os, time, importlib.util, pathlib, multiprocessing as mp
import cv2

# --- 공통: DLL 경로 주입 (최상위) ---
def _add_cv2_dll_dir():
    spec = importlib.util.find_spec("cv2")
    if spec and spec.submodule_search_locations and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(pathlib.Path(list(spec.submodule_search_locations)[0])))

# --- 실제 프로브 작업 (자식 프로세스에서 실행) ---
def _probe_child_main(q, spec, backend, w, h, fourcc, warmup, read_wait):
    try:
        _add_cv2_dll_dir()
        cap = cv2.VideoCapture(spec, backend)
        if not cap.isOpened():
            q.put(False); return
        try:
            if fourcc:
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
        t_end = time.time() + read_wait*(warmup+1) + 0.3
        ok = False
        while time.time() < t_end:
            r, frame = cap.read()
            if r and frame is not None:
                ok = True
                break
            time.sleep(0.02)
        cap.release()
        q.put(ok)
    except Exception:
        q.put(False)

# --- 타임아웃 래퍼 (최상위 함수) ---
def _probe_with_timeout(spec, backend, timeout=1.2, w=640, h=480, fourcc="MJPG", warmup=3, read_wait=0.25):
    ctx = mp.get_context("spawn")            # 글로벌 set_start_method 불필요/권장
    q = ctx.SimpleQueue()                    # picklable
    p = ctx.Process(
        target=_probe_child_main,
        args=(q, spec, backend, w, h, fourcc, warmup, read_wait),
        daemon=True,
    )
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate(); p.join(0.2)
        return False
    try:
        return bool(q.get_nowait())
    except Exception:
        return False

# --- 카메라 검색/오픈 (예시) ---
def discover_cameras(max_idx=8, total_timeout=8.0):
    _add_cv2_dll_dir()
    start = time.time()
    BACKENDS = [cv2.CAP_DSHOW, cv2.CAP_FFMPEG, cv2.CAP_ANY]  # 설치본 안정 순서
    found = []
    for idx in range(0, max_idx):
        for be in BACKENDS:
            if time.time() - start > total_timeout:
                return found
            if _probe_with_timeout(idx, be, timeout=1.2):
                found.append((idx, be))
                break
    return found

def open_camera(max_idx=8, total_timeout=8.0):
    cands = discover_cameras(max_idx=max_idx, total_timeout=total_timeout)
    for idx, be in cands:
        cap = cv2.VideoCapture(idx, be)
        if cap.isOpened():
            return cap
    return None
