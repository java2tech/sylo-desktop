
import flet as ft

from components.body_shape_background import BodyShapeBackground
from variables import Colors, Gender, StorageKeys
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
    # page.client_storage.set("body-shape", BodyShape["FEMALE"]["H"])
    gender = page.client_storage.get(StorageKeys["GENDER"])
    title = ft.Container(
        content=ft.Text(
            "체형을 분석합니다",
            size=48,
            color=Colors["TEXT_WHITE"],
            font_family="SUIT-SemiBold",
            text_align=ft.TextAlign.CENTER,
            expand=True,
        ),
        height=58,
        margin=ft.margin.only(bottom=15),
    )
    message = ft.Container(
        content=ft.Image(
            src="images/lineMessage.png",
            width=321,
            height=41,
            fit=ft.ImageFit.COVER,
        ),
        margin=ft.margin.only(bottom=43),
    )
    body_line_img_male = ft.Image(
        src="images/maleBody.svg",
        width=237,
        height=650,
        fit=ft.ImageFit.COVER,
    )
    body_line_img_female = ft.Image(
        src="images/femaleBody.svg",
        width=289,
        height=654,
        fit=ft.ImageFit.COVER,
    )
    body_line_img = body_line_img_male if gender == Gender["MALE"] else body_line_img_female
    def handle_click_go_back(e: ft.TapEvent):
        page.go("/select-gender")
        page.update()
    go_back_btn = GoBackButton(on_click=handle_click_go_back)
    container = ft.Container(
        expand=True,
        content=ft.Stack(
            fit=ft.StackFit.EXPAND,
            controls=[
                ft.Container(expand=True, alignment=ft.alignment.center, content=body_line_img),
                ft.Container(expand=True, alignment=ft.alignment.center_left, content=go_back_btn),
            ],
        ),
        height=650 if gender == "male" else 654,
    )
    overlay = ft.Container(
                content=ft.Column(
                    controls=[
                        title,
                        message,
                        container,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                ),
                padding=20,
                expand=True,
                bgcolor=COLORS.with_opacity(0.25, "#231f20"),
            )
    async def on_fixed_shape(shape: str, measures: dict):
        print(f"Fixed shape: {shape}, measures: {measures}")
        await page.client_storage.set_async(StorageKeys["BODY-SHAPE"], shape)
        page.go("/scan-result")
        page.update()
    return ft.View(
        route="/",
        controls=[
            BodyShapeBackground(
                overlay=overlay,
                gender=gender,
                enable_segmentation=True,
                show_distance_label=False,     # 폭 숫자 숨김
                show_info_panel=False,         # 좌상단 정보 패널 숨김
                show_reason_text=False,
                stable_secs=3.0,
                on_shape_stable=on_fixed_shape, 
            ),
        ],
        padding=0,
    )
