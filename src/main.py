import flet as ft
from components.splash_screen import show_splash_screen

Router = None

def dump_opencv_diagnostics():
    from pathlib import Path
    import os, cv2, sys
    cv2_dir = Path(cv2.__file__).parent
    txt = [
        f"cv2.__version__ = {cv2.__version__}",
        f"cv2.__file__    = {cv2.__file__}",
        f"PLUGIN_PATH env = {os.environ.get('OPENCV_VIDEOIO_PLUGIN_PATH')}",
        "videoio plugins = " + ", ".join([p.name for p in cv2_dir.glob("opencv_videoio_ffmpeg*")]),
    ]
    Path.home().joinpath("opencv_debug.txt").write_text("\n".join(txt), encoding="utf-8")

def _ensure_router():
    import os, sys
    dump_opencv_diagnostics()
    if getattr(sys, "frozen", False):
        from pathlib import Path
        import cv2  # 플러그인 로드는 아직 안 됨 - 경로만 확인
        cv2_dir = Path(cv2.__file__).parent
        # 1) OpenCV에 플러그인 위치 알려주기
        os.environ.setdefault("OPENCV_VIDEOIO_PLUGIN_PATH", str(cv2_dir))
        # 2) Windows DLL 검색 경로에 cv2 폴더 추가 (Py 3.8+)
        if hasattr(os, "add_dll_directory"):
            _h = os.add_dll_directory(str(cv2_dir))
            # 핸들이 GC 되면 경로가 해제되므로 보관
            globals()["_cv2_dll_dir_handle"] = _h
        # 3) (선택) 기본 우선순위를 Windows 카메라 스택(MSMF/DShow) 위주로
        os.environ.setdefault("OPENCV_VIDEOIO_PRIORITY_MSMF", "10000")
        os.environ.setdefault("OPENCV_VIDEOIO_PRIORITY_DSHOW", "9000")
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
