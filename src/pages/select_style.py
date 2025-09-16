
import flet as ft

from components.camera_background import CameraBackground
from variables import Colors, StorageKeys
from components.button import GoBackButton

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
    gender = page.client_storage.get(StorageKeys["GENDER"])
    fitting_type = page.client_storage.get(StorageKeys["FITTING-TYPE"])
    title = ft.Container(
        content=ft.Text(
            "추천 스타일",
            size=48,
            color=Colors["TEXT_WHITE"],
            font_family="SUIT-SemiBold",
            text_align=ft.TextAlign.CENTER,
            expand=True,
        ),
        height=58,
        margin=ft.margin.only(bottom=35),
    )
    desc = ft.Container(
        content=ft.Text(
            "원하는 스타일을 선택하세요",
            size=36,
            color=COLORS.with_opacity(0.75, Colors["TEXT_WHITE"]),
            font_family="SUIT-Medium",
            text_align=ft.TextAlign.CENTER,
        ),
        margin=ft.margin.only(bottom=51),
    )
    def handle_click_go_back(e: ft.TapEvent):
        page.go("/select-fitting-type")
    go_back_btn = GoBackButton(on_click=handle_click_go_back)
    
    def SelectStyleBtn(image_path: str, on_click=None):
        return ft.Container(
            width=114,
            height=202,
            border_radius=24,
            bgcolor=Colors["TEXT_WHITE"],
            content=ft.Image(
                src=image_path,
                width=114,
                height=202,
                fit=ft.ImageFit.COVER,
            ),
            on_click=on_click,
        )
    gender = page.client_storage.get(StorageKeys["GENDER"])
    bodyShape = page.client_storage.get(StorageKeys["BODY-SHAPE"])
    def handle_click_style(idx: int):
        page.client_storage.set(StorageKeys["FITTING_IMAGE_PATH"], f"images/fitting/{fitting_type}/{gender}/{bodyShape}/{idx}.png")
        page.go("/fitting-view")
    styles_row = ft.Row(
        controls=[
            SelectStyleBtn(f"images/{fitting_type}/{gender}/{bodyShape}/{idx}.png", on_click=lambda e, idx=idx: handle_click_style(idx)) for idx in range(1, 7)
        ],
        wrap=True,
        width=376,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=16,
    )
    container = ft.Container(
        content=ft.Stack(
            expand=True,
            controls=[
                ft.Container(expand=True, alignment=ft.alignment.center, content=styles_row),
                ft.Container(expand=True, alignment=ft.alignment.center_left, content=go_back_btn),
            ],
        ),
    )
    overlay = ft.Container(
                content=ft.Column(
                    controls=[
                        title,
                        desc,
                        container,
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
