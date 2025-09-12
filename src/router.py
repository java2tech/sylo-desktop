import re
from urllib.parse import urlparse, parse_qs
import flet as ft

from pages import intro, input_name, select_gender, scan_body, select_fitting_type, select_style, select_color, send_image, next_menu, scan_result

class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self._routes = [
            (re.compile(r"^/$"), self._build_root),
            (re.compile(r"^/input-name/?$"), self._build_input_name),
            (re.compile(r"^/select-gender/?$"), self._build_select_gender),
            (re.compile(r"^/scan-body/?$"), self._build_scan_body),
            (re.compile(r"^/select-fitting-type/?$"), self._build_select_fitting_type),
            (re.compile(r"^/select-style/?$"), self._build_select_style),
            (re.compile(r"^/select-color/?$"), self._build_select_color),
            (re.compile(r"^/send-image/?$"), self._build_send_image),
            (re.compile(r"^/next-menu/?$"), self._build_next_menu),
            (re.compile(r"^/scan-result/?$"), self._build_scan_result),
        ]

    def view_pop(self, e: ft.ViewPopEvent):
        if self.page.views:
            self.page.views.pop()
        self.page.go(self.page.views[-1].route if self.page.views else "/")

    def route_change(self, e: ft.RouteChangeEvent):
        url = urlparse(e.route or "/")
        path = url.path or "/"
        qdict = {k: v[0] if isinstance(v, list) else v for k, v in parse_qs(url.query).items()}
        for pattern, builder in self._routes:
            m = pattern.match(path)
            if m:
                params = m.groupdict()
                views = builder(path=path, q=qdict, params=params)
                self._replace_views(views)
                return
        # views = self._build_not_found(path=path)
        # self._replace_views(views)

    # 현재 뷰 스택 교체
    def _replace_views(self, views: list[ft.View]):
        self.page.views.clear()
        self.page.views.extend(views)
        self.page.update()

    def _build_root(self, path: str, q: dict, params: dict):
        return [intro.view(self.page)]
    
    def _build_input_name(self, path: str, q: dict, params: dict):
        return [input_name.view(self.page)]
    
    def _build_select_gender(self, path: str, q: dict, params: dict):
        return [select_gender.view(self.page)]
    
    def _build_scan_body(self, path: str, q: dict, params: dict):
        return [scan_body.view(self.page)]
    
    def _build_select_fitting_type(self, path: str, q: dict, params: dict):
        return [select_fitting_type.view(self.page)]
    
    def _build_select_style(self, path: str, q: dict, params: dict):
        return [select_style.view(self.page)]
    
    def _build_select_color(self, path: str, q: dict, params: dict):
        return [select_color.view(self.page)]
    
    def _build_send_image(self, path: str, q: dict, params: dict):
        return [send_image.view(self.page)]

    def _build_next_menu(self, path: str, q: dict, params: dict):
        return [next_menu.view(self.page)]
    
    def _build_scan_result(self, path: str, q: dict, params: dict):
        return [scan_result.view(self.page)]
    