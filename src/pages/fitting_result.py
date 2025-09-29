
import flet as ft

from components.camera_background import CameraBackground
from variables import Colors, StorageKeys, BLANK_B64
from components.button import GoBackButton, ImageButton

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
    username = page.client_storage.get(StorageKeys["USERNAME"])
    gender = page.client_storage.get(StorageKeys["GENDER"])
    title = ft.Container(
        content=ft.Text(
            "Sylo 스타일링 완료",
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
            f"{username}님의 결과를 확인하세요",
            size=36,
            color=COLORS.with_opacity(0.75, Colors["TEXT_WHITE"]),
            font_family="SUIT-Medium",
            text_align=ft.TextAlign.CENTER,
        ),
        margin=ft.margin.only(bottom=51),
    )
    def handle_click_go_back(e: ft.TapEvent):
        # page.go("/select-gender")
        page.go("/select-fitting-type")
        page.update()
    go_back_btn = GoBackButton(on_click=handle_click_go_back)
    
    def SelectStyleBtn(image_b64: str):
        return ft.Container(
            width=169,
            height=298,
            border_radius=24,
            bgcolor=Colors["TEXT_WHITE"],
            content=ft.Image(
                src_base64=image_b64,
                width=114,
                height=202,
                fit=ft.ImageFit.COVER,
            ),
        )
    result_images = [
        page.client_storage.get(StorageKeys["FITTING-RESULT-IMAGE-BASE64-1"]) or BLANK_B64,
        page.client_storage.get(StorageKeys["FITTING-RESULT-IMAGE-BASE64-2"]) or BLANK_B64,
        page.client_storage.get(StorageKeys["FITTING-RESULT-IMAGE-BASE64-3"]) or BLANK_B64,
        page.client_storage.get(StorageKeys["FITTING-RESULT-IMAGE-BASE64-4"]) or BLANK_B64,
    ]
    styles_row = ft.Row(
        controls=[
            SelectStyleBtn(b64) for b64 in result_images
        ],
        wrap=True,
        width=348,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )
    def handle_click_export(e: ft.TapEvent):
        print("Export clicked")
        page.go("/send-image")
        page.update()
    def handle_click_home(e: ft.TapEvent):
        page.go("/")
        page.update()
    btns = ft.Container(
        padding=22,
        content=ft.Column(
            expand=True,
            height=560,
            controls=[ft.Column(
                controls=[
                    ImageButton(src="images/exportButton.png", width=48, height=48, on_click=handle_click_export),
                    ImageButton(src="images/homeButton.png", width=48, height=48, on_click=handle_click_home),
                ],
                spacing=9,
                width=48,
            )],
            alignment=ft.MainAxisAlignment.START,
        ),
    )
    container = ft.Container(
        content=ft.Row(
            controls=[
                styles_row,
                btns,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
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
        route="/fitting-result",
        controls=[
            CameraBackground(overlay=overlay),
        ],
        padding=0,
    )
