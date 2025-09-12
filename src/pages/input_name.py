import flet as ft

from components.camera_background import CameraBackground
from components.textbox import Textbox
from variables import Colors, StorageKeys

from utils.keyboard import show_touch_keyboard, hide_touch_keyboard

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
            "Sylo가 불러줄\n당신의 이름",
            size=48,
            color=Colors["TEXT_WHITE"],
            font_family="SUIT-SemiBold",
        ),
        margin=ft.margin.only(bottom=63),
    )
    rule = ft.Container(
        content=ft.Text(
            "한글 최대 5자/ 영어, 한문, 특수기호 불가",
            size=24,
            color=COLORS.with_opacity(0.75, Colors["TEXT_WHITE"]),
            font_family="SUIT-Medium",
        ),
        margin=ft.margin.only(bottom=74),
    )
    def handle_submit(e: ft.ControlEvent):
        username = e.control.value.strip()
        page.client_storage.set(StorageKeys["USERNAME"], username)
        page.go("/select-gender")
        page.update()
    textbox = ft.Container(
        content=Textbox(hint="이름을 입력해주세요", on_submit=handle_submit),
        margin=ft.margin.only(bottom=41),
    )
    overlay = ft.Container(
                content=ft.Column(
                    controls=[
                        title,
                        rule,
                        textbox,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
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
