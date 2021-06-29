import os
import random
import logging

import requests

import docker

from backend.applications.application_containers import ApplicationContainers
from backend.route.routing_statistics import RoutingStatistics
from backend.route.route_config import RouteConfig
from flask import Flask, Response, send_from_directory
from flask import request as flask_request


class BackendDestinationNotAvailable(Exception):
    """Raised when no running container found for backend application."""


class Router:
    def __init__(self, config: RouteConfig):
        self.config = config
        self.docker_client = docker.from_env()
        self._routing_stats_generator = RoutingStatistics()
        self._app_containers = ApplicationContainers(self.docker_client)
        self.app = Flask(__name__)
        self.app.add_url_rule(
            rule="/<path:path>",
            view_func=self.backend_route,
            methods=["GET", "POST"],
        )
        self.app.add_url_rule(
            rule="/stats",
            view_func=self.run_stats,
            methods=["GET"],
        )
        self.app.before_request(self._before)
        self.app.after_request(self._after)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel("DEBUG")

    def validate_path(self, path_prefix) -> None:
        self.logger.debug(f"routes: {self.config.routes}")
        if path_prefix not in self.config.routes:
            raise ValueError(f"Invalid path_prefix: {path_prefix}")

    def get_backend_app_container(self, path_prefix: str):
        self.validate_path(path_prefix)
        app_identifier = self.config.routes.get(path_prefix)
        containers = self._app_containers.get_app_container_by_labels(app_identifier.labels)
        if not containers:
            raise BackendDestinationNotAvailable(f"No running containers found for path {path_prefix}")
        self.logger.debug("Containers found.")
        return random.choice(containers)

    def make_request(self, url: str) -> Response:
        self.logger.debug(f"Making request to {url}")
        backend_response = requests.request(
            method=flask_request.method,
            url=url,
            data=flask_request.data,
            headers=flask_request.headers
        )
        self.logger.debug(f"Backend response {backend_response}")
        return Response(
            response=backend_response.content,
            status=backend_response.status_code,
            headers=[(n, v) for (n, v) in backend_response.raw.headers.items()]
        )

    def run_stats(self):
        return self._routing_stats_generator.stats

    def favicon(self):
        return send_from_directory(
            os.path.join(self.app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon"
        )

    def backend_route(self, **kwargs):
        if flask_request.path == "/favicon.ico":
            return self.favicon()
        try:
            container = self.get_backend_app_container(flask_request.path)
        except ValueError as e:
            if e.args[0] == "Invalid path_prefix":
                self.logger.error(e)
                return self.config.default_response
            raise
        except BackendDestinationNotAvailable:
            self.logger.debug("")
            return Response(response="Backend application not available.", status=503)
        self.logger.debug(f"Got a container: {container}")
        endpoint_base_url = self._app_containers.get_container_endpoint(container.id)
        self.logger.debug(f"Got a endpoint_base_url: {endpoint_base_url}")
        return self.make_request(endpoint_base_url)

    def _before(self, **kwargs):
        self.logger.debug("Starting route")
        self._routing_stats_generator.start_timer()

    def _after(self, response: Response):
        self.logger.debug(f"Routing complete, response: {response}")
        self._routing_stats_generator.stop_timer()
        self._routing_stats_generator.log(response)
        return response

    def run(self):
        self.app.run()
