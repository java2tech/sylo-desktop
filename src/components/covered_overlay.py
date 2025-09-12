import flet as ft
from typing import Optional


class CoveredOverlay(ft.Stack):
    def __init__(
        self,
        src: str,
        overlay: ft.Control,
        *,
        overlay_alignment: ft.alignment.Alignment = ft.alignment.center,
        scrim_color: Optional[str] = None,
        scrim_opacity: float = 0.0,
        padding=None,
        **kwargs,
    ):
        # 배경 레이어 (이미지 COVER)
        self._bg = ft.Container(
            expand=True,
            image_src=src,
            image_fit=ft.ImageFit.COVER,
        )

        # 스크림 레이어 (선택)
        self._scrim = ft.Container(expand=True)
        if scrim_color and scrim_opacity > 0:
            self._scrim.bgcolor = ft.colors.with_opacity(scrim_opacity, scrim_color)

        # 오버레이 레이어
        self._overlay = ft.Container(
            expand=True,
            alignment=overlay_alignment,
            padding=padding,
            content=overlay,
        )

        layers = [self._bg, self._scrim, self._overlay]

        # Stack 초기화
        super().__init__(controls=layers, **kwargs)

    # --- 편의 프로퍼티/메서드 ---

    @property
    def src(self) -> str:
        """현재 배경 이미지 경로"""
        return self._bg.image_src

    @src.setter
    def src(self, value: str) -> None:
        self._bg.image_src = value
        self.update()

    @property
    def overlay(self) -> ft.Control:
        """현재 오버레이 컨트롤"""
        return self._overlay.content

    @overlay.setter
    def overlay(self, value: ft.Control) -> None:
        self._overlay.content = value
        self.update()

    def set_overlay_alignment(self, alignment: ft.alignment.Alignment) -> None:
        """오버레이 정렬 변경"""
        self._overlay.alignment = alignment
        self.update()

    def set_scrim(self, color: Optional[str], opacity: float = 0.0) -> None:
        """스크림 색/투명도 설정(0이면 미적용)"""
        if color and opacity > 0:
            self._scrim.bgcolor = ft.colors.with_opacity(opacity, color)
        else:
            self._scrim.bgcolor = None
        self.update()
