import random
import requests

import docker

from backend.applications.application_containers import ApplicationContainers
from backend.route.route_config import RouteConfig
from flask import Flask, Response
from flask import request as flask_request

app = Flask(__name__)


class NoActiveDestinationForPath(Exception):
    """Raised when no running container found for backend application."""


class Router:
    def __init__(self, config: RouteConfig):
        self.config = config
        self.docker_client = docker.from_env()
        self._app_containers = ApplicationContainers(self.docker_client)

    def validate_path(self, path_prefix) -> None:
        if path_prefix not in self.config.routes:
            raise ValueError("Invalid path_prefix")

    def get_backend_app_container(self, path_prefix: str):
        self.validate_path(path_prefix)
        app_identifier = self.config.routes.get(path_prefix)
        containers = self._app_containers.get_app_container_by_labels(app_identifier.labels)
        if not containers:
            raise NoActiveDestinationForPath(f"No running containers found for path {path_prefix}")
        return random.choice(containers)

    @classmethod
    def make_request(cls, url: str):
        if flask_request.method == "GET":
            r = requests.get(url, **flask_request.args)
            return Response(r.content)
        elif flask_request.method == "POST":
            r = requests.post(url, **flask_request.args)
            return Response(r.content)

    @app.route("/")
    def run_stats(self):
        ...

    @app.route("/<path_prefix>", methods=["GET", "POST"])
    def run_backend_app(self, path_prefix):
        try:
            container = self.get_backend_app_container(path_prefix)
        except ValueError as e:
            if e.args[0] == "Invalid path_prefix":
                return self.config.default_response
            raise
        except NoActiveDestinationForPath:
            return Response(response="Backend application not available.", status=503)

        endpoint_base_url = self._app_containers.get_container_endpoint(container.id)
        return self.make_request(endpoint_base_url)
