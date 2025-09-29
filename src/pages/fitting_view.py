
import flet as ft

from variables import Colors, StorageKeys
from components.button import GoBackButton, ImageButton
from components.fitting_container import FittingContainer

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
    fitting_image_path = page.client_storage.get(StorageKeys["FITTING_IMAGE_PATH"])
    title = ft.Container(
        content=ft.Text(
            "가상 피팅 미리보기",
            size=48,
            color=Colors["TEXT_WHITE"],
            font_family="SUIT-SemiBold",
            text_align=ft.TextAlign.CENTER,
            expand=True,
        ),
        height=58,
        margin=ft.margin.only(bottom=35),
    )
    def handle_click_go_back(e: ft.TapEvent):
        page.go("/select-style")
        page.update()
    fitting_container = FittingContainer(
                    overlay_path="./assets/"+ fitting_image_path,
                    width=348,
                    height=615,
                    fps=12,
                )
    def get_current_fitting_result_idx():
        idx = 1
        for i in range(1, 5):
            if page.client_storage.get(StorageKeys[f"FITTING-RESULT-IMAGE-BASE64-{i}"]) is None:
                idx = i
                break
        return idx
    def handle_click_save(e: ft.TapEvent):
        base64 = fitting_container.get_last_frame_base64()
        current_idx = get_current_fitting_result_idx()
        page.client_storage.set(StorageKeys[f"FITTING-RESULT-IMAGE-BASE64-{current_idx}"], base64)
        page.go("/next-menu")
        page.update()
    go_back_btn = GoBackButton(on_click=handle_click_go_back)
    styles_row = ft.Row(
        controls=[
            go_back_btn,
            ft.Container(
                width=348,
                height=615,
                border_radius=24,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                content=fitting_container,
            ),
            ft.Column(
                controls=[
                    ImageButton(src="images/saveButton.png", width=61, height=62, on_click=lambda e: handle_click_save(e)),
                ],
                alignment=ft.MainAxisAlignment.END,
                height=615,
            ),
        ],
        spacing=25,
    )
    overlay = ft.Container(
                content=ft.Column(
                    controls=[
                        title,
                        styles_row,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                ),
                padding=20,
                expand=True,
                bgcolor="#231f20",
            )
    return ft.View(
        route="/fitting-view",
        controls=[
            overlay,
        ],
        padding=0,
    )
