import numpy as np
import mediapipe as mp
import flet as ft
import asyncio
import base64
import time
from typing import Optional, Tuple
import cv2
from collections import deque
from dataclasses import dataclass
from typing import Optional, Tuple, Callable, Awaitable
from utils.camera import open_camera

PIXEL_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4n"
    "GNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)

@dataclass
class _Measures:
    shoulder: float = 0.0
    pelvis: float = 0.0
    waist: float = 0.0
    abdomen: float = 0.0
    y_waist: int = 0
    y_abdomen: int = 0
    xw0: int = 0; xw1: int = 0
    xa0: int = 0; xa1: int = 0

class BodyShapeBackground(ft.Stack):
    """
    Flet 이미지 위젯에 실시간 카메라 프레임을 올리고,
    MediaPipe Pose + Segmentation으로 체형(H/O/Y/A/X) 추정 결과를 프레임에 그려서 표시합니다.
    """
    def __init__(
        self,
        overlay: ft.Container,
        fps: int = 24,
        cam_index_hint: int = 0,
        gender: str = "male",
        enable_segmentation: bool = True,
        show_distance_label: bool = False,
        show_info_panel: bool = False,
        show_reason_text: bool = False,
        # ▼ 추가
        stable_secs: float = 3.0,
        on_shape_stable: Optional[Callable[[str, dict], None | Awaitable[None]]] = None,
    ):
        super().__init__()
        self.expand = True
        self.fit = ft.StackFit.EXPAND
        self.fps = fps
        self.cam_index_hint = cam_index_hint
        self.gender = "female" if str(gender).lower().startswith("f") else "male"
        self.enable_segmentation = enable_segmentation

        self.running: bool = False
        self.paused: bool = False
        self.mirror: bool = True
        self.cap: Optional[cv2.VideoCapture] = None
        self.last_frame = None

        # smoothing
        self._s_hist = deque(maxlen=12)
        self._h_hist = deque(maxlen=12)
        self._w_hist = deque(maxlen=12)
        self._a_hist = deque(maxlen=12)

        # heuristics thresholds
        self.THRESH = dict(
            INV_TRIANGLE=1.12,   # S/H, S/W (Y형)
            PEAR=1.12,           # H/S (A형)
            HOURGLASS_WAIST=0.78,
            O_ABDOMEN=1.08,      # A / max(S,H)
            O_WAIST_MALE=0.92,   # W / mean(S,H)
            O_WAIST_FEMALE=0.90
        )

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            model_complexity=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
            smooth_landmarks=True,
            enable_segmentation=self.enable_segmentation,
        )

        self.video = ft.Container(
            content=ft.Image(
                src_base64=PIXEL_BASE64,
                fit=ft.ImageFit.COVER,
                gapless_playback=True,
            ),
            expand=True,
            width=None,
            height=None,
        )
        self.fps_text = ft.Text("0 fps", size=12, opacity=0.85)
        self.controls = [
            self.video,
            ft.Container(content=self.fps_text, alignment=ft.alignment.bottom_left, padding=6),
            overlay,
        ]
        self.show_distance_label = show_distance_label
        self.show_info_panel = show_info_panel
        self.show_reason_text = show_reason_text
        self.stable_secs = float(stable_secs)
        self.on_shape_stable = on_shape_stable
        self._shape_last: Optional[str] = None
        self._shape_last_change_ts: float = 0.0
        self._shape_fired_for: set[str] = set()

    async def _maybe_fire_stable(self, shape: str, measures: dict):
        """
        shape가 self.stable_secs 동안 변하지 않았으면 on_shape_stable 호출.
        on_shape_stable 이 async이면 task로 실행, sync면 즉시 호출.
        동일 shape에 대해서는 상태가 바뀌기 전까지 1회만 호출.
        """
        if not shape or shape == "UNKNOWN" or self.on_shape_stable is None:
            return

        now = time.time()
        if self._shape_last != shape:
            # 상태 변경: 타이머 리셋 및 fired 기록 초기화 조건
            self._shape_last = shape
            self._shape_last_change_ts = now
            # 상태가 바뀌면 동일 shape 재안정을 위해 fired 기록에서 제거
            # (그 전 shape가 아니라 방금 shape를 지울 필요는 없음 — 아래 로직은 set 체크로 처리)
            return

        # 같은 상태 유지 중
        if (now - self._shape_last_change_ts) >= self.stable_secs:
            if shape not in self._shape_fired_for:
                cb = self.on_shape_stable
                try:
                    if asyncio.iscoroutinefunction(cb):
                        # Flet 이벤트 루프에서 안전하게 태스크로 실행
                        await cb(shape, measures)
                    else:
                        cb(shape, measures)
                except Exception as e:
                    # 안전을 위해 콘솔에만 기록
                    print(f"[on_shape_stable error] {e}")
                finally:
                    self._shape_fired_for.add(shape)  # 동일 상태 재호출 방지

    # ----------------- Flet lifecycle -----------------
    def did_mount(self):
        self.running = True
        self.page.run_task(self._camera_loop)

    def will_unmount(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        try:
            self.pose.close()
        except Exception:
            pass

    # ----------------- Geometry helpers -----------------
    @staticmethod
    def _euclidean(p1, p2, w, h) -> float:
        x1, y1 = int(p1.x * w), int(p1.y * h)
        x2, y2 = int(p2.x * w), int(p2.y * h)
        return float(np.hypot(x2 - x1, y2 - y1))

    @staticmethod
    def _largest_run_width(row_binary):
        xs = np.where(row_binary)[0]
        if xs.size < 2:
            return 0, 0, 0
        splits = np.where(np.diff(xs) > 1)[0]
        starts = np.r_[xs[0], xs[splits + 1]]
        ends   = np.r_[xs[splits], xs[-1]]
        lens   = ends - starts + 1
        k = np.argmax(lens)
        return int(lens[k]), int(starts[k]), int(ends[k])

    @classmethod
    def _width_from_mask(cls, binary_mask, y, pad=2):
        h, w = binary_mask.shape
        y0 = max(0, y - pad)
        y1 = min(h - 1, y + pad)
        if y0 >= h or y1 < 0:
            return 0, 0, 0
        row = binary_mask[y0:y1 + 1, :]
        col_any = np.max(row, axis=0) > 0
        width, x0, x1 = cls._largest_run_width(col_any)
        return width, x0, x1

    @classmethod
    def _profile_min_max(cls, binary_mask, y_top, y_bottom, y_step=4, pad=2):
        h, _ = binary_mask.shape
        y_top = max(0, min(h - 1, int(y_top)))
        y_bottom = max(0, min(h - 1, int(y_bottom)))
        if y_top > y_bottom:
            y_top, y_bottom = y_bottom, y_top
        min_w = 10**9; min_pos = (0, 0, 0, y_top)
        max_w = 0;     max_pos = (0, 0, 0, y_top)
        for y in range(y_top, y_bottom + 1, y_step):
            w, x0, x1 = cls._width_from_mask(binary_mask, y, pad=pad)
            if w > 0 and w < min_w:
                min_w, min_pos = w, (w, x0, x1, y)
            if w > max_w:
                max_w, max_pos = w, (w, x0, x1, y)
        return min_pos, max_pos  # (w,x0,x1,y)

    def _smooth_append(self, deq: deque, val: float) -> float:
        if val > 0:
            deq.append(val)
        return float(np.mean(deq)) if len(deq) else val

    @staticmethod
    def _draw_width_overlay(frame, y, x0, x1, label, color=(0, 255, 0), draw_text=False):
        if x1 > x0 and 0 <= y < frame.shape[0]:
            cv2.line(frame, (x0, y), (x1, y), color, 2)
            if draw_text:  # ← 기본 False
                cv2.putText(frame, f"{label}:{x1 - x0}px",
                            (x0, max(0, y - 6)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, color, 1, cv2.LINE_AA)

    # ----------------- Shape classification -----------------
    def _classify_shape(self, S: float, H: float, W: float, A: float) -> Tuple[str, str]:
        eps = 1e-6
        if min(S, H, W) < eps:
            return "UNKNOWN", "전신이 프레임에 충분히 보이지 않음."
        meanSH = (S + H) / 2.0
        shoulder_hip = S / (H + eps)
        hip_shoulder = H / (S + eps)
        waist_mean = W / (meanSH + eps)
        abdomen_max = A / max(S, H, eps)
        abd_vs_waist = A / (W + eps)

        info = f"어깨/골반={shoulder_hip:.2f}, 허리/평균={waist_mean:.2f}, 복부/최대={abdomen_max:.2f}"

        if shoulder_hip >= self.THRESH['INV_TRIANGLE'] and (S / (W + eps)) >= self.THRESH['INV_TRIANGLE']:
            return "Y", "어깨가 골반·허리보다 넓음. " + info

        o_waist_thr = self.THRESH['O_WAIST_MALE'] if self.gender == "male" else self.THRESH['O_WAIST_FEMALE']
        if abdomen_max >= self.THRESH['O_ABDOMEN'] and waist_mean >= o_waist_thr and abd_vs_waist >= 1.06:
            return "O", "복부가 두드러지고 허리 굴곡이 작음. " + info

        if self.gender == 'female':
            if hip_shoulder >= self.THRESH['PEAR'] and (W / (H + eps)) <= 0.85:
                return "A", "골반>어깨, 허리가 잘록. " + info
            if abs(shoulder_hip - 1.0) <= 0.08 and waist_mean <= self.THRESH['HOURGLASS_WAIST']:
                return "X", "어깨≈골반, 허리가 잘록. " + info

        return "H", "어깨≈골반, 허리 굴곡이 크지 않음(또는 기타 조건 미충족). " + info

    # ----------------- Main async camera loop -----------------
    async def _camera_loop(self):
        self.fps_text.value = "Opening camera..."
        self.fps_text.update()
        self.cap = await open_camera()
        if not self.cap:
            self.fps_text.value = "Camera open failed (check device/permission)"
            self.fps_text.color = "red"
            self.fps_text.update()
            self.page.update()
            return
        else:
            self.page.update()

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]  # 전송량 줄이기
        last_sec = time.time()
        frame_counter = 0

        while self.running:
            if not self.paused:
                ok, frame = self.cap.read()
                if not ok:
                    await asyncio.sleep(0.02)
                    continue
                if self.mirror:
                    frame = cv2.flip(frame, 1)

                h, w = frame.shape[:2]
                output = frame.copy()

                # ---- Pose inference ----
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_rgb.flags.writeable = False
                results = self.pose.process(image_rgb)
                image_rgb.flags.writeable = True

                measure = _Measures()

                # ---- Optional: background blur with segmentation (visual) ----
                if self.enable_segmentation and results.segmentation_mask is not None:
                    condition = (np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1)
                    bg_image = cv2.GaussianBlur(output, (55, 55), 0)
                    output = np.where(condition, output, bg_image)

                # ---- Landmarks + measurement ----
                if results.pose_landmarks:
                    lm = results.pose_landmarks.landmark
                    LSH = lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    RSH = lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                    LHP = lm[self.mp_pose.PoseLandmark.LEFT_HIP.value]
                    RHP = lm[self.mp_pose.PoseLandmark.RIGHT_HIP.value]

                    vis_ok = (LSH.visibility > 0.5 and RSH.visibility > 0.5 and
                              LHP.visibility > 0.5 and RHP.visibility > 0.5)

                    if vis_ok:
                        S = self._euclidean(LSH, RSH, w, h)
                        Hpel = self._euclidean(LHP, RHP, w, h)
                        y_sh = int(((LSH.y + RSH.y) / 2.0) * h)
                        y_hp = int(((LHP.y + RHP.y) / 2.0) * h)

                        # 기본값
                        W_val, A_val = 0.0, 0.0
                        y_w = y_a = int((y_sh + y_hp) / 2)
                        xw0 = xw1 = xa0 = xa1 = int(w/2)

                        if self.enable_segmentation and results.segmentation_mask is not None and y_hp > y_sh + 10:
                            # segmentation mask -> binary -> morphology
                            mask = results.segmentation_mask
                            binmask = (mask > 0.3).astype(np.uint8) * 255
                            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                            binmask = cv2.morphologyEx(binmask, cv2.MORPH_OPEN, kernel, iterations=1)
                            binmask = cv2.morphologyEx(binmask, cv2.MORPH_CLOSE, kernel, iterations=2)

                            torso = (y_hp - y_sh)
                            # 허리: 상부-중부 사이의 최소 폭
                            yW_top = y_sh + int(0.45 * torso)
                            yW_bot = y_sh + int(0.75 * torso)
                            # 복부: 허리 아래쪽 최대 폭
                            yA_top = y_sh + int(0.60 * torso)
                            yA_bot = y_sh + int(0.88 * torso)

                            (w_min, xw0, xw1, y_w), _ = self._profile_min_max(binmask, yW_top, yW_bot, y_step=3, pad=2)
                            _, (w_max, xa0, xa1, y_a) = self._profile_min_max(binmask, yA_top, yA_bot, y_step=3, pad=2)
                            W_val = float(w_min)
                            A_val = float(w_max)
                        else:
                            # 세그멘테이션이 없거나 범위가 불안정: 임시 추정
                            W_val = S * 0.75
                            A_val = max(S, Hpel) * 0.95
                            y_w = int(y_sh + 0.6 * (y_hp - y_sh))
                            y_a = int(y_sh + 0.75 * (y_hp - y_sh))
                            xw0, xw1 = int(w/2 - W_val/2), int(w/2 + W_val/2)
                            xa0, xa1 = int(w/2 - A_val/2), int(w/2 + A_val/2)

                        # smoothing
                        S_s = self._smooth_append(self._s_hist, S)
                        H_s = self._smooth_append(self._h_hist, Hpel)
                        W_s = self._smooth_append(self._w_hist, W_val)
                        A_s = self._smooth_append(self._a_hist, A_val)

                        # classify
                        shape, reason = self._classify_shape(S_s, H_s, W_s, A_s)
                        
                        measures_dict = {
                            "shoulder": S_s,
                            "pelvis": H_s,
                            "waist": W_s,
                            "abdomen": A_s,
                        }
                        await self._maybe_fire_stable(shape, measures_dict)
                        # draw pose
                        self.mp_drawing.draw_landmarks(
                            output, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                            landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                            connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2),
                        )
                        # shoulder/hip lines
                        cv2.line(output, (int(LSH.x*w), int(LSH.y*h)), (int(RSH.x*w), int(RSH.y*h)), (255,0,0), 2)
                        cv2.line(output, (int(LHP.x*w), int(LHP.y*h)), (int(RHP.x*w), int(RHP.y*h)), (0,165,255), 2)

                        # width overlays
                        self._draw_width_overlay(output, y_w, int(xw0), int(xw1), "Waist", (0,255,0),
                                                draw_text=self.show_distance_label)
                        self._draw_width_overlay(output, y_a, int(xa0), int(xa1), "Abd",   (0,200,255),
                                                draw_text=self.show_distance_label)

                    else:
                        # 가시성 낮음 분기
                        self._shape_last = None
                        self._shape_last_change_ts = 0.0
                        self._shape_fired_for.clear()
                else:
                    # 사람 미검출 분기
                    self._shape_last = None
                    self._shape_last_change_ts = 0.0
                    self._shape_fired_for.clear()

                # ---- push to Flet Image ----
                self.last_frame = output
                ok, jpg = cv2.imencode(".jpg", output, encode_param)
                if ok:
                    b64 = base64.b64encode(jpg).decode("ascii")
                    self.video.content.src_base64 = b64
                    self.video.content.update()

                frame_counter += 1
                now = time.time()
                if now - last_sec >= 1.0:
                    self.fps_text.value = f"{frame_counter} fps"
                    self.fps_text.update()
                    frame_counter = 0
                    last_sec = now

            await asyncio.sleep(1 / max(1, self.fps))

        if self.cap:
            self.cap.release()
            self.cap = None

    def quit_app(self, _):
        self.page.window.close()
