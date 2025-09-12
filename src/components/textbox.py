import flet as ft
from variables import Colors

COLORS = getattr(ft, "Colors", None)
if COLORS is None:
    class _ColorsFallback:
        BLACK = "black"
        SURFACE_CONTAINER_HIGHEST = "surfaceContainerHighest"
        @staticmethod
        def with_opacity(opacity: float, color: str):
            return f"{color},{opacity}"
    COLORS = _ColorsFallback()

def Textbox(hint: str, on_submit=None, on_focus=None, on_blur=None) -> ft.TextField:
    return ft.TextField(
            hint_text=hint,
            hint_style=ft.TextStyle(
                font_family="SUIT-Medium",
                color=COLORS.with_opacity(0.5, Colors["TEXT_WHITE"]),
            ),
            text_size=36,
            border=ft.InputBorder.NONE,
            text_style=ft.TextStyle(
                font_family="SUIT-Medium",
                color=Colors["TEXT_WHITE"],
            ),
            autofocus=True,
            on_focus=on_focus,
            on_blur=on_blur,
            on_submit=on_submit,
    )
