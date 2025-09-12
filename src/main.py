import flet as ft

from router import Router

def main(page: ft.Page):
    page.title = "Sylo"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.expand = True
    page.bgcolor = "black"
    page.fonts = {
        "SUIT-Thin": "fonts/SUIT/SUIT-Thin.ttf",
        "SUIT-Regular": "fonts/SUIT/SUIT-Regular.ttf",
        "SUIT-Medium": "fonts/SUIT/SUIT-Medium.ttf",
        "SUIT-SemiBold": "fonts/SUIT/SUIT-SemiBold.ttf",
        "SUIT-Bold": "fonts/SUIT/SUIT-Bold.ttf",
    }
    page.window.width = 595
    page.window.height = 1000
    page.window.resizable = False
    page.window.maximizable = False
    router = Router(page)
    page.on_route_change = router.route_change
    page.on_view_pop = router.view_pop
    page.go("/scan-result")

    # cam_layer = CameraBackground(fps=24, cam_index_hint=0)

"""     def on_close(_):
        cam_layer.running = False
        if cam_layer.cap:
            cam_layer.cap.release()

    page.on_close = on_close
    page.add(cam_layer) """


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
