from typing import List, Dict

from flask import Response
from backend.route.utils import Route, ApplicationIdentifiers


class RouteConfig:
    def __init__(
            self, routes: List[Route], app_identifiers: List[ApplicationIdentifiers], default_response: Response
    ) -> None:
        self._routes = routes
        self._app_identifiers = app_identifiers
        self.default_response = default_response
        self._app_map = {a.name: a for a in self._app_identifiers}
        self.validate()

    @property
    def routes(self) -> Dict[str, ApplicationIdentifiers]:
        return {route.path_prefix: self._app_map[route.backend] for route in self._routes}

    def validate(self) -> None:
        for route in self._routes:
            if route.backend not in self._app_map:
                raise ValueError(f"Route {route.backend} doesn't have corresponding application in app_identifiers")

