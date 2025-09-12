
import flet as ft

from components.camera_background import CameraBackground
from variables import Colors, Gender, BodyShape, StorageKeys, BodyStyles
from components.button import GoBackButton

def RecommendBox(label: str, value: str):
    return ft.Container(
        width=481,
        height=143,
        content=ft.Stack(
            expand=True,
            controls=[
                ft.Image(
                    src="images/recommendBackground.png",
                    fit=ft.ImageFit.COVER,
                    expand=True
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                label,
                                size=21,
                                color=Colors["TEXT_WHITE"],
                                font_family="SUIT-SemiBold",
                                text_align=ft.TextAlign.LEFT,
                            ),
                            ft.Text(
                                value,
                                size=24,
                                color=Colors["TEXT_WHITE"],
                                font_family="SUIT-Medium",
                                text_align=ft.TextAlign.LEFT,
                            )
                        ],  
                    ),
                    padding=ft.padding.only(left=37, right=37, top=22, bottom=22),
                )
            ]
        ),
    )

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
    # username = page.client_storage.get(StorageKeys["USERNAME"])
    # page.client_storage.set(StorageKeys["BODY-SHAPE"], BodyShape["FEMALE"]["H"])
    # bodyShape = page.client_storage.get(StorageKeys["BODY-SHAPE"])
    username = "김형진"
    bodyShape = "O"
    gender = "MALE"
    #gender =  page.client_storage.get(StorageKeys["GENDER"])
    title = ft.Container(
        content=ft.Text(
            f"{username}님은 {bodyShape}체형입니다",
            size=48,
            color=Colors["TEXT_WHITE"],
            font_family="SUIT-SemiBold",
            text_align=ft.TextAlign.CENTER,
            expand=True,
        ),
        height=58,
        margin=ft.margin.only(bottom=15),
    )
    desc = ft.Container(
        content=ft.Text(
            BodyStyles[gender][bodyShape].get()["desc"],
            size=24,
            color=Colors["TEXT_WHITE"],
            font_family="SUIT-SemiBold",
            text_align=ft.TextAlign.CENTER,
        ),
        margin=ft.margin.only(bottom=5),
    )
    hashtags = ft.Container(
        content=ft.Text(
            BodyStyles[gender][bodyShape].get()["hashtag"],
            size=30,
            color=COLORS.with_opacity(0.6, Colors["TEXT_WHITE"]),
            font_family="SUIT-Regular",
            text_align=ft.TextAlign.CENTER,
        ),
        margin=ft.margin.only(bottom=15),
    )
    recommend_box = RecommendBox(label="< 추천 스타일 >", value=BodyStyles[gender][bodyShape].get()["recommend"])
    ignore_box = RecommendBox(label="< 이런 스타일은 피하세요! >", value=BodyStyles[gender][bodyShape].get()["ignore"])
    boxes = ft.Column(
        controls=[
            recommend_box,
            ignore_box,
        ],
        spacing=15,
    )
    overlay = ft.Container(
                content=ft.Column(
                    controls=[
                        title,
                        desc,
                        hashtags,
                        boxes,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                ),
                padding=20,
                expand=True,
                bgcolor=COLORS.with_opacity(0.25, "#231f20"),
            )
    return ft.View(
        route="/scan-result",
        controls=[
            CameraBackground(overlay=overlay),
        ],
        padding=0,
    )
