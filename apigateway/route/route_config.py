from __future__ import annotations
from typing import List, Dict, Any

from flask import Response
from apigateway.route.utils import Route, ApplicationIdentifiers


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

    @classmethod
    def parse(cls, config_dict: Dict[str, Any]) -> RouteConfig:
        routes = [
            Route(path_prefix=route_config["path_prefix"], backend=route_config["backend"])
            for route_config in config_dict.get("routes")
        ]
        app_identifiers = [
            ApplicationIdentifiers(name=backend_config["name"], matched_labels=backend_config["match_labels"])
            for backend_config in config_dict.get("backends")
        ]
        default_response = Response(
            response=config_dict["default_response"]["body"],
            status=config_dict["default_response"]["status_code"]
        )
        return cls(routes, app_identifiers, default_response)
