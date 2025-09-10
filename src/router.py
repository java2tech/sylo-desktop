import re
from urllib.parse import urlparse, parse_qs
import flet as ft

from pages import intro

class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self._routes = [
            (re.compile(r"^/$"), self._build_root),
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
        views = self._build_not_found(path=path)
        self._replace_views(views)

    # 현재 뷰 스택 교체
    def _replace_views(self, views: list[ft.View]):
        self.page.views.clear()
        self.page.views.extend(views)
        self.page.update()

    def _build_root(self, path: str, q: dict, params: dict):
        return [intro.view(self.page)]
