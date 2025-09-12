import flet as ft

from components.camera_background import CameraBackground
from variables import Colors, StorageKeys
from components.button import ImageButton

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
            "체형에 맞는\n스타일링을 시작합니다",
            size=48,
            color=Colors["TEXT_WHITE"],
            font_family="SUIT-SemiBold",
            text_align=ft.TextAlign.LEFT,
            width=436
        ),
        margin=ft.margin.only(bottom=63),
    )
    desc = ft.Container(
        content=ft.Text(
            "원하는 타입을 선택하세요",
            size=36,
            color=COLORS.with_opacity(0.75, Colors["TEXT_WHITE"]),
            font_family="SUIT-Medium",
            text_align=ft.TextAlign.LEFT,
            width=432,
        ),
        margin=ft.margin.only(bottom=102),
    )
    def handle_select_type(type: str):
        page.client_storage.set(StorageKeys["FITTING-TYPE"], type)
        page.go("/select-style")
        page.update()
    photo_btn = ImageButton(src="images/photoButton.png", width=187, height=221, on_click=lambda e: handle_select_type("photo"))
    illustration_btn = ImageButton(src="images/illustrationButton.png", width=187, height=221, on_click=lambda e: handle_select_type("illustration"))
    select = ft.Row(
        controls=[
            illustration_btn,
            photo_btn,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=50,
    )
    overlay = ft.Container(
                content=ft.Column(
                    controls=[
                        title,
                        desc,
                        select,
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