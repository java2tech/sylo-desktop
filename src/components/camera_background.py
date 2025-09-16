import numpy as np
import mediapipe as mp
import flet as ft
import asyncio
import base64
import time
from typing import Optional, Tuple
import cv2

PIXEL_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4n"
    "GNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)

class CameraBackground(ft.Stack):
    def __init__(self, overlay: ft.Container, fps: int = 24, cam_index_hint: int = 0):
        super().__init__()
        self.expand = True
        self.fit = ft.StackFit.EXPAND
        self.fps = fps
        self.cam_index_hint = cam_index_hint

        self.running: bool = False
        self.paused: bool = False
        self.mirror: bool = True
        self.cap: Optional[cv2.VideoCapture] = None
        self.last_frame = None
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            enable_segmentation=True,
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
        self.fps_text = ft.Text("0 fps", size=12, opacity=0.8)
        self.controls = [
            self.video,
                        ft.Container(
                content=self.fps_text, alignment=ft.alignment.bottom_left, padding=5
            ),
            overlay,
        ]

    # 수명주기: 화면에 올라온 직후 백그라운드 루프 시작
    def did_mount(self):
        self.running = True
        self.page.run_task(self._camera_loop)

    # 수명주기: 제거 직전 자원 해제
    def will_unmount(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    async def _open_camera(self) -> Tuple[Optional[cv2.VideoCapture], Optional[int], Optional[int]]:
        BACKENDS = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        candidates = [self.cam_index_hint] + [i for i in range(0, 6) if i != self.cam_index_hint]
        for idx in candidates:
            for be in BACKENDS:
                cap = cv2.VideoCapture(idx, be)
                if cap.isOpened():
                    for _ in range(6):
                        cap.read()
                        await asyncio.sleep(0.01)
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    ok, _ = cap.read()
                    if ok:
                        return cap, idx, be
                cap.release()
        return None, None, None

    async def _camera_loop(self):
        self.fps_text.value = "Opening camera..."
        self.fps_text.update()
        self.cap, used_idx, used_be = await self._open_camera()
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

                # BGR 이미지를 RGB로 변환
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_rgb.flags.writeable = False

                # MediaPipe Pose로 처리
                results = self.pose.process(image_rgb)

                image_rgb.flags.writeable = True
                output_frame = frame.copy()

                # 세그멘테이션 마스크 그리기 (배경 블러 처리)
                if results.segmentation_mask is not None:
                    condition = (
                        np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
                    )
                    bg_image = cv2.GaussianBlur(output_frame, (55, 55), 0)
                    output_frame = np.where(condition, output_frame, bg_image)

                # Pose 랜드마크 그리기
                if results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        output_frame,
                        results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                            color=(245, 117, 66), thickness=2, circle_radius=2
                        ),
                        connection_drawing_spec=self.mp_drawing.DrawingSpec(
                            color=(245, 66, 230), thickness=2, circle_radius=2
                        ),
                    )

                self.last_frame = output_frame
                ok, jpg = cv2.imencode(".jpg", output_frame, encode_param)
                if ok:
                    b64 = base64.b64encode(jpg).decode("ascii")
                    self.video.content.src_base64 = b64
                    self.video.update()
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
