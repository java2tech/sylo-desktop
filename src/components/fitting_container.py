# fitting_container.py
# -*- coding: utf-8 -*-
import base64
import asyncio
import time
import math
import os
from typing import Optional, Tuple

import cv2
import numpy as np
import flet as ft

# ==== 투명 1x1 PNG (placeholder) ====
TRANSPARENT_1PX_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO2xG9kAAAAASUVORK5CYII="
)

# mediapipe
try:
    import mediapipe as mp
except ImportError:
    raise SystemExit("`pip install mediapipe` 후 다시 실행하세요.")


class FittingContainer(ft.Image): # Inherit from ft.Image
    """
    Flet용 가상 피팅 컨테이너 (ft.Image 기반)
    - 피팅 PNG(투명 배경)를 어깨/엉덩이 포즈에 맞춰 합성
    - 시스템 카메라 자동 탐색 → 미러 표시
    - 컨테이너 높이에 맞춰 스케일, 가로 가운데 정렬 + 필요시 좌우 크롭 (비율 유지)
    """

    # ==== 동작 파라미터 (필요시 조정) ====
    CAM_WIDTH = 1280
    CAM_HEIGHT = 720
    CAMERA_SEARCH_RANGE = list(range(0, 8))

    VIS_TH = 0.60
    SMOOTH_ALPHA = 0.25

    WIDTH_SCALE = 1.60
    HEIGHT_SCALE = 2.40
    XOFF_RATIO = 0.00
    YOFF_RATIO = -0.10
    OPACITY = 1
    ANGLE_BIAS_DEG = 0.0
    ANCHOR_TOP_RATIO = 0.08

    JPEG_QUALITY = 75

    def __init__(
        self,
        overlay_path: str,
        width: int,
        height: int,
        fps: int = 24,
        **kwargs,
    ):
        super().__init__(
            width=width,
            height=height,
            src_base64=TRANSPARENT_1PX_PNG_B64,
            fit=ft.ImageFit.FILL,
            repeat=ft.ImageRepeat.NO_REPEAT,
            **kwargs,
        )
        self.overlay_path = overlay_path
        self.width_px = int(width)
        self.height_px = int(height)
        self.fps = fps

        # 내부 상태
        self._stop_event = asyncio.Event()
        self._cap: Optional[cv2.VideoCapture] = None
        self._pose: Optional[mp.solutions.pose.Pose] = None

        self._sm_sh_center = None
        self._sm_sh_dist = None
        self._sm_torso_len = None
        self._sm_angle_deg = None

        # 오버레이 이미지
        self._overlay_rgba = self._load_rgba_image(self.overlay_path)
        
        # Use a default white background for cropping, as ft.Image has no bgcolor
        self._bg_bgr = (255, 255, 255)

    # ==== Flet lifecycle ====
    def did_mount(self):
        self._stop_event.clear()
        self.page.run_task(self._run_loop)

    def will_unmount(self):
        self._stop_event.set()
        try:
            if self._cap:
                self._cap.release()
        except Exception:
            pass
        try:
            if self._pose:
                self._pose.close()
        except Exception:
            pass

    # ==== 메인 루프 ====
    async def _run_loop(self):
        cap = self._find_working_camera(self.CAMERA_SEARCH_RANGE)
        if cap is None:
            self._show_text_frame("No camera found")
            return

        self._cap = cap

        pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        self._pose = pose

        last_t = 0.0
        target_interval = 1.0 / float(self.fps)

        while not self._stop_event.is_set():
            ok, frame = cap.read()
            if not ok or frame is None:
                await asyncio.sleep(0.01)
                continue

            proc = frame
            
            results = pose.process(cv2.cvtColor(proc, cv2.COLOR_BGR2RGB))
            metrics = self._extract_pose_metrics(results, proc.shape, self.VIS_TH)

            if metrics is not None:
                sh_center = np.array(metrics["shoulder_center"], dtype=np.float32)
                sh_dist = float(metrics["shoulder_dist"])
                torso_len = float(metrics["torso_len"])
                angle_deg = float(metrics["angle_deg"])

                self._sm_sh_center = self._ema(self._sm_sh_center, sh_center, self.SMOOTH_ALPHA) if self._sm_sh_center is not None else sh_center
                self._sm_sh_dist   = self._ema(self._sm_sh_dist, sh_dist, self.SMOOTH_ALPHA) if self._sm_sh_dist is not None else sh_dist
                self._sm_torso_len = self._ema(self._sm_torso_len, torso_len, self.SMOOTH_ALPHA) if self._sm_torso_len is not None else torso_len
                self._sm_angle_deg = self._angle_smooth(self._sm_angle_deg, angle_deg, self.SMOOTH_ALPHA)

                if self._overlay_rgba is not None and self._sm_sh_dist and self._sm_torso_len:
                    if self._sm_sh_dist > 5 and self._sm_torso_len > 5:
                        target_w = self._sm_sh_dist * self.WIDTH_SCALE
                        target_h = self._sm_torso_len * self.HEIGHT_SCALE

                        ov0 = self._overlay_rgba
                        oh0, ow0 = ov0.shape[:2]
                        scale_w = target_w / float(ow0)
                        scale_h = target_h / float(oh0)
                        scale = max(scale_w, scale_h)
                        scale = max(scale, 0.01)

                        new_w = max(1, int(round(ow0 * scale)))
                        new_h = max(1, int(round(oh0 * scale)))
                        ov_scaled = cv2.resize(ov0, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

                        anchor_local = np.array([new_w / 2.0, new_h * self.ANCHOR_TOP_RATIO], dtype=np.float32)

                        angle_total = (self._sm_angle_deg if self._sm_angle_deg is not None else 0.0) + self.ANGLE_BIAS_DEG
                        ov_rot, M = self._rotate_bound_bgra(ov_scaled, angle_total)
                        anchor_rot = self._transform_points(M, [anchor_local])[0]

                        xoff_px = self.XOFF_RATIO * self._sm_sh_dist
                        yoff_px = self.YOFF_RATIO * self._sm_torso_len
                        target_anchor = (float(self._sm_sh_center[0] + xoff_px), float(self._sm_sh_center[1] + yoff_px))

                        top_left = (int(round(target_anchor[0] - anchor_rot[0])),
                                    int(round(target_anchor[1] - anchor_rot[1])))

                        proc = self._overlay_bgra_on_bgr(proc, ov_rot, top_left, global_opacity=self.OPACITY)

            show = cv2.flip(proc, 1)
            display = self._fit_by_height_center_crop(show, self.width_px, self.height_px, self._bg_bgr)
            self._push_frame(display)

            now = time.time()
            elapsed = now - last_t
            if elapsed < target_interval:
                await asyncio.sleep(target_interval - elapsed)
            last_t = now

        if self._cap:
            self._cap.release()
        if self._pose:
            self._pose.close()

    def _push_frame(self, img_bgr: np.ndarray):
        try:
            ok, buf = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), self.JPEG_QUALITY])
            if not ok:
                return
            b64 = base64.b64encode(buf).decode("utf-8")
            
            self.src_base64 = b64
            self.update()
        except Exception:
            pass

    def _show_text_frame(self, text: str):
        canvas = np.full((self.height_px, self.width_px, 3), self._bg_bgr, dtype=np.uint8)
        cv2.putText(canvas, text, (20, self.height_px // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
        self._push_frame(canvas)

    def _find_working_camera(self, indices):
        BACKENDS = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        for idx in indices:
            for be in BACKENDS:
                cap = cv2.VideoCapture(idx, be)
                if cap.isOpened():
                    for _ in range(6):
                        cap.read()
                        time.sleep(0.01)
                    
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAM_WIDTH)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAM_HEIGHT)
                    ok, frame = cap.read()
                    
                    if ok and frame is not None:
                        return cap
                
                cap.release()
        return None

    @staticmethod
    def _ensure_bgra(img):
        if img is None:
            return None
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
        elif img.shape[2] == 3:
            alpha = np.full((img.shape[0], img.shape[1], 1), 255, dtype=np.uint8)
            img = np.concatenate([img, alpha], axis=2)
        return img

    def _load_rgba_image(self, path: str):
        if not path or not os.path.exists(path):
            return None
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        return self._ensure_bgra(img)

    @staticmethod
    def _rotate_bound_bgra(image, angle_deg):
        (h, w) = image.shape[:2]
        (cX, cY) = (w / 2.0, h / 2.0)
        M = cv2.getRotationMatrix2D((cX, cY), angle_deg, 1.0)
        cos = abs(M[0, 0]); sin = abs(M[0, 1])
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
        M[0, 2] += (nW / 2.0) - cX
        M[1, 2] += (nH / 2.0) - cY
        rotated = cv2.warpAffine(
            image, M, (nW, nH),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0)
        )
        return rotated, M

    @staticmethod
    def _transform_points(M, points_xy):
        pts = np.array(points_xy, dtype=np.float32).reshape(-1, 2)
        ones = np.ones((pts.shape[0], 1), dtype=np.float32)
        pts_h = np.hstack([pts, ones])
        out = pts_h @ M.T
        return out

    @staticmethod
    def _overlay_bgra_on_bgr(base_bgr, overlay_bgra, top_left_xy, global_opacity=1.0):
        x, y = int(top_left_xy[0]), int(top_left_xy[1])
        if overlay_bgra is None:
            return base_bgr
        h, w = overlay_bgra.shape[:2]
        H, W = base_bgr.shape[:2]
        x1 = max(x, 0); y1 = max(y, 0)
        x2 = min(x + w, W); y2 = min(y + h, H)
        if x1 >= x2 or y1 >= y2:
            return base_bgr
        ov = overlay_bgra[(y1 - y):(y2 - y), (x1 - x):(x2 - x), :]
        bg = base_bgr[y1:y2, x1:x2, :]
        alpha = ov[:, :, 3:4].astype(np.float32) / 255.0
        alpha = np.clip(alpha * float(global_opacity), 0.0, 1.0)
        ov_rgb = ov[:, :, :3].astype(np.float32)
        bg_rgb = bg.astype(np.float32)
        out = alpha * ov_rgb + (1.0 - alpha) * bg_rgb
        base_bgr[y1:y2, x1:x2, :] = out.astype(np.uint8)
        return base_bgr

    @staticmethod
    def _dist(p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    @staticmethod
    def _ema(prev, cur, alpha):
        if prev is None:
            return cur
        return prev * (1.0 - alpha) + cur * alpha

    @staticmethod
    def _angle_smooth(prev_deg, cur_deg, alpha):
        if prev_deg is None:
            return cur_deg
        delta = cur_deg - prev_deg
        while delta > 180.0:
            cur_deg -= 360.0
            delta = cur_deg - prev_deg
        while delta < -180.0:
            cur_deg += 360.0
            delta = cur_deg - prev_deg
        return (prev_deg * (1.0 - alpha) + cur_deg * alpha)

    @staticmethod
    def _canonicalize_angle_deg(a):
        a = (a + 180.0) % 360.0 - 180.0
        if a > 90.0:
            a -= 180.0
        elif a <= -90.0:
            a += 180.0
        return a

    def _extract_pose_metrics(self, results, frame_shape, vis_th=0.6):
        H, W = frame_shape[:2]
        if not results or not results.pose_landmarks:
            return None
        lm = results.pose_landmarks.landmark

        def get_xyv(idx):
            p = lm[idx]
            return (p.x * W, p.y * H, p.visibility)

        PoseLandmark = mp.solutions.pose.PoseLandmark
        LSH = PoseLandmark.LEFT_SHOULDER.value
        RSH = PoseLandmark.RIGHT_SHOULDER.value
        LHP = PoseLandmark.LEFT_HIP.value
        RHP = PoseLandmark.RIGHT_HIP.value

        lx, ly, lv = get_xyv(LSH)
        rx, ry, rv = get_xyv(RSH)
        hx1, hy1, hv1 = get_xyv(LHP)
        hx2, hy2, hv2 = get_xyv(RHP)

        if min(lv, rv, hv1, hv2) < vis_th:
            return None

        left_shoulder = (lx, ly)
        right_shoulder = (rx, ry)
        shoulder_center = ((lx + rx) / 2.0, (ly + ry) / 2.0)
        hip_center = ((hx1 + hx2) / 2.0, (hy1 + hy2) / 2.0)
        shoulder_dist = self._dist(left_shoulder, right_shoulder)
        torso_len = self._dist(shoulder_center, hip_center)

        if lx <= rx:
            xL, yL = lx, ly
            xR, yR = rx, ry
        else:
            xL, yL = rx, ry
            xR, yR = lx, ly
        angle_rad = math.atan2((yR - yL), (xR - xL))
        angle_deg = self._canonicalize_angle_deg(math.degrees(angle_rad))

        return {
            "left_shoulder": left_shoulder,
            "right_shoulder": right_shoulder,
            "shoulder_center": shoulder_center,
            "hip_center": hip_center,
            "shoulder_dist": shoulder_dist,
            "torso_len": torso_len,
            "angle_deg": angle_deg,
        }

    @staticmethod
    def _parse_color_to_bgr(color) -> Tuple[int, int, int]:
        if isinstance(color, str) and color.startswith("#") and (len(color) in (7, 9)):
            if len(color) == 9:
                rr = color[3:5]; gg = color[5:7]; bb = color[7:9]
            else:
                rr = color[1:3]; gg = color[3:5]; bb = color[5:7]
            try:
                r = int(rr, 16); g = int(gg, 16); b = int(bb, 16)
                return (b, g, r)
            except Exception:
                pass
        return (255, 255, 255)

    @staticmethod
    def _fit_by_height_center_crop(img_bgr: np.ndarray, out_w: int, out_h: int, bg_bgr=(255, 255, 255)) -> np.ndarray:
        h, w = img_bgr.shape[:2]
        if h == 0 or w == 0:
            return np.full((out_h, out_w, 3), bg_bgr, dtype=np.uint8)
        scale = out_h / float(h)
        new_w = max(1, int(round(w * scale)))
        resized = cv2.resize(img_bgr, (new_w, out_h), interpolation=cv2.INTER_LINEAR if scale >= 1.0 else cv2.INTER_AREA)

        if new_w >= out_w:
            x = (new_w - out_w) // 2
            return resized[:, x:x + out_w].copy()
        else:
            canvas = np.full((out_h, out_w, 3), bg_bgr, dtype=np.uint8)
            x = (out_w - new_w) // 2
            canvas[:, x:x + new_w] = resized
            return canvas