
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
            "색상을 선택하세요",
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
        # page.go("/select-gender")
        page.go("/select-fitting-type")
        page.update()
    go_back_btn = GoBackButton(on_click=handle_click_go_back)
    def SelectColorBtn(bgcolor: str):
        return ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.CLICK,
            content=ft.Container(
                width=25,
                height=25,
                bgcolor=bgcolor,
                border_radius=12.5,
            )
        )
    styles_row = ft.Row(
        controls=[
            go_back_btn,
            ft.Container(
                width=348,
                height=615,
                border_radius=24,
                bgcolor=Colors["TEXT_WHITE"],
            ),
            ft.Column(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(
                                            "상의",
                                            size=18,
                                            color=Colors["TEXT_WHITE"],
                                            font_family="SUIT-SemiBold",
                                            text_align=ft.TextAlign.LEFT,
                                        ),
                                        padding=ft.padding.only(top=17),
                                        margin=ft.margin.only(bottom=11),
                                    ),
                                    ft.Column(
                                        controls=[
                                            SelectColorBtn(Colors['TEXT_WHITE']),
                                            SelectColorBtn(Colors["TEXT_WHITE"]),
                                            SelectColorBtn(Colors["TEXT_WHITE"]),
                                            SelectColorBtn(Colors["TEXT_WHITE"]),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    )
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(
                                            "하의",
                                            size=18,
                                            color=Colors["TEXT_WHITE"],
                                            font_family="SUIT-SemiBold",
                                            text_align=ft.TextAlign.LEFT,
                                        ),
                                        padding=ft.padding.only(top=31),
                                        margin=ft.margin.only(bottom=11),
                                    ),
                                    ft.Column(
                                        controls=[
                                            SelectColorBtn(Colors["TEXT_WHITE"]),
                                            SelectColorBtn(Colors["TEXT_WHITE"]),
                                            SelectColorBtn(Colors["TEXT_WHITE"]),
                                            SelectColorBtn(Colors["TEXT_WHITE"]),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    )
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ImageButton(src="images/saveButton.png", width=61, height=62),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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
                bgcolor=COLORS.with_opacity(0.75, "#231f20"),
            )
    return ft.View(
        route="/",
        controls=[
            CameraBackground(overlay=overlay),
        ],
        padding=0,
    )
