import flet as ft

def ImageButton(src, on_click=None, width=270, height=74):
    return ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.CLICK,
        on_tap=on_click,
        content=ft.Container(
            content=ft.Image(src, fit=ft.ImageFit.COVER),
            width=width,
            height=height,
            border_radius=12,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ink=True,
        )
    )

def GoBackButton(on_click=None):
    return ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.CLICK,
        on_tap=on_click,
        content=ft.Container(
            content=ft.Image("images/goBackButton.png", fit=ft.ImageFit.COVER),
            width=79,
            height=79,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ink=True,
        )
    )

def Button(label: str = "시작하기", on_click=None, width=180, height=50):
    text = ft.Text(
        label,
        color="white",
        size=36,
        font_family="SUIT-Bold",
    )

    container = ft.Container(
        width=width,
        height=height,
        alignment=ft.alignment.center,
        border_radius=14,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#8FA0B8", "#6E7F99"],
        ),
        shadow=[
            ft.BoxShadow(
                blur_radius=14,
                spread_radius=0,
                color="rgba(0,0,0,0.35)",
                offset=ft.Offset(0, 6),
            ),
            ft.BoxShadow(
                blur_radius=14,
                spread_radius=0,
                color="rgba(255,255,255,0.25)",
                offset=ft.Offset(0, -3),
            ),
        ],
        animate_scale=ft.Animation(200, "easeOut"),  # ✅ animate=... 대신 animate_scale 사용
        content=text,
    )

    # hover & click 핸들러
    def handle_click(e: ft.ControlEvent):
        container.scale = 0.95
        container.update()
        container.scale = 1.0
        container.update()
        if callable(on_click):
            on_click(e)

    def handle_hover(e: ft.HoverEvent):
        if e.data == "true":
            container.scale = 1.05
        else:
            container.scale = 1.0
        container.update()

    container.on_click = handle_click
    container.on_hover = handle_hover

    return container