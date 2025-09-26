import flet as ft

def show_splash_screen(page: ft.Page):
    page.controls.clear()
    page.add(
        ft.Container(
            width=page.window.width,
            height=page.window.height,
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    ft.Image(
                        src="images/loading.gif",
                        width=400,
                        height=400,
                        fit=ft.ImageFit.COVER,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            bgcolor="#231F20",
        )
    )
    page.update()
