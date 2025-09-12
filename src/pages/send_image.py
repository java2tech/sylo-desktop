import flet as ft

from components.camera_background import CameraBackground
from components.textbox import Textbox
from variables import Colors, StorageKeys

ICONS = getattr(ft, "Icons", None)
if ICONS is None:
    from flet import icons as ICONS

COLORS = getattr(ft, "Colors", None)
if COLORS is None:
    class _ColorsFallback:
        BLACK = "black"
        SURFACE_CONTAINER_HIGHEST = "surfaceContainerHighest"
        @staticmethod
        def with_opacity(opacity: float, color: str):
            return f"{color},{opacity}"
    COLORS = _ColorsFallback()

def view(page: ft.Page) -> ft.View:
    title = ft.Container(
        content=ft.Text(
            "체형 결과와 함께\n이미지 전송해드릴게요",
            size=48,
            color=Colors["TEXT_WHITE"],
            font_family="SUIT-SemiBold",
        ),
        width=436,
        margin=ft.margin.only(bottom=63),
    )
    rule = ft.Container(
        content=ft.Text(
            "이메일을 입력해주세요",
            size=24,
            color=COLORS.with_opacity(0.75, Colors["TEXT_WHITE"]),
            font_family="SUIT-Medium",
        ),
        width=436,
        margin=ft.margin.only(bottom=74),
    )
    def handle_submit(e: ft.ControlEvent):
        username = e.control.value.strip()
        page.client_storage.set(StorageKeys["USERNAME"], username)
        page.go("/select-gender")
        page.update()
    textbox = ft.Container(
        width=436,
        content=Textbox(
            hint="example@email.com",
            on_submit=handle_submit,
        ),
        margin=ft.margin.only(bottom=168),
    )
    notice = ft.Container(
        width=436,
        content=ft.Text(
            "* 개인정보는 이미지 공유 후 삭제됩니다",
            size=12,
            color=COLORS.with_opacity(0.5, Colors["TEXT_WHITE"]),
            font_family="SUIT-Medium",
            text_align=ft.TextAlign.CENTER,
        ),
    )
    overlay = ft.Container(
        content=ft.Column(
            controls=[
                title,
                rule,
                textbox,
                notice,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
        padding=20,
        expand=True,
        bgcolor=COLORS.with_opacity(0.75, "#231f20"),
    )
    return ft.View(
        route="/",
        controls=[
            CameraBackground(overlay=overlay),
        ],
        padding=0,
    )
