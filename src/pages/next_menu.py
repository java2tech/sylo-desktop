
import flet as ft

from components.camera_background import CameraBackground
from variables import Colors, StorageKeys
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
    gender = page.client_storage.get(StorageKeys["GENDER"])
    title = ft.Container(
        content=ft.Text(
            "저장하시겠습니까?",
            size=48,
            color=Colors["TEXT_WHITE"],
            font_family="SUIT-SemiBold",
            text_align=ft.TextAlign.CENTER,
            expand=True,
        ),
        height=58,
        margin=ft.margin.only(bottom=49),
    )
    select_more_btn = ft.Container(
        content=ImageButton(
            src="images/selectMoreButton.png",
            width=270,
            height=74,
            on_click=lambda e: print("more select"),
        ),
        margin=ft.margin.only(bottom=29),
    )
    check_report_btn = ft.Container(
        content=ImageButton(
            src="images/checkReportButton.png",
            width=270,
            height=74,
            on_click=lambda e: page.go("/select-color"),
        ),
    )
    overlay = ft.Container(
                content=ft.Column(
                    controls=[
                        title,
                        select_more_btn,
                        check_report_btn,
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
