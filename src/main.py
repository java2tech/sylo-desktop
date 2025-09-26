import flet as ft
from components.splash_screen import show_splash_screen

Router = None

def _ensure_router():
    import importlib.util, pathlib, os
    spec = importlib.util.find_spec("cv2")
    if spec and spec.submodule_search_locations:
        cv2_dir = pathlib.Path(list(spec.submodule_search_locations)[0])
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(cv2_dir))
    global Router
    if Router is None:
        import importlib
        Router = importlib.import_module("router").Router

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
    show_splash_screen(page)
    _ensure_router()
    page.controls.clear()
    router = Router(page)
    page.on_route_change = router.route_change
    page.on_view_pop = router.view_pop
    page.go(page.route or "/")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
