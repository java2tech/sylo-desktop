import flet as ft

from components.camera_background import CameraBackground

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

from components.button import ImageButton

def view(page: ft.Page) -> ft.View:
    page.client_storage.clear()
    def handle_click_start_btn(e: ft.TapEvent):
        print("Start button clicked!")
        page.go("/input-name")
        page.update()
    start_button = ImageButton(src="images/startButton.png", width=270, height=74, on_click=handle_click_start_btn)
    logo = ft.Image(src="images/logo.svg", width=276, height=173)
    description = ft.Container(
        content=ft.Text(
            "Style이 곧 Life가 되는 순간",
            size=36,
            color="white",
            font_family="SUIT-SemiBold",
        ),
        margin=ft.margin.only(top=48,bottom=87),
    )
    overlay = ft.Container(
                content=ft.Column(
                    controls=[
                        logo,
                        description,
                        start_button
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
