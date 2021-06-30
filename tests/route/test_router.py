import json
from unittest.mock import MagicMock, patch
import requests
import docker
from docker.models.containers import Container
import pytest as pytest

from apigateway.route.application_containers import ApplicationContainers
from apigateway.route.route_config import RouteConfig
from apigateway.route.router import Router


class TestRouter:
    @pytest.fixture
    def mock_container(self):
        mock_container = MagicMock(spec=Container)
        mock_container.id = "container_1"
        return mock_container

    @pytest.fixture
    def mock_docker(self, mock_container):
        mock_docker = MagicMock(spec=docker)
        mock_docker.from_env.return_value.containers.list.return_value = [mock_container]
        mock_docker.APIClient.return_value.inspect_container.return_value = {
            "NetworkSettings": {
                "Ports": {"80tcp": [{"HostIp": "0.0.0.0", "HostPort": "8080"}]}
            }
        }
        return mock_docker

    @pytest.fixture
    def mock_requests_success(self):
        mock_requests = MagicMock(spec=requests)
        mock_response = MagicMock()
        mock_response.content = "success"
        mock_response.status_code = 200
        mock_response.raw.headers = {}
        mock_requests.request.return_value = mock_response
        return mock_requests

    @pytest.fixture
    def mock_requests_failure(self):
        mock_requests = MagicMock(spec=requests)
        mock_response = MagicMock()
        mock_response.content = "Service Unavailabl"
        mock_response.status_code = 503
        mock_response.raw.headers = {}
        mock_requests.request.return_value = mock_response
        return mock_requests

    @pytest.fixture
    def config_dict(self):
        return {
            "routes": [
                {"path_prefix": "/api/payment", "backend": "payment"},
                {"path_prefix": "/api/orders", "backend": "orders"}
            ],
            "default_response": {
                "body": "This is not reachable",
                "status_code": 403
            },
            "backends": [
                {"name": "payment", "match_labels": ["app_name=payment", "env=production"]},
                {"name": "orders", "match_labels": ["app_name=orders", "env=production"]}
            ]
        }

    @pytest.fixture
    def route_config(self, config_dict):
        return RouteConfig.parse(config_dict)

    @pytest.fixture
    def router(self, mock_docker, route_config, mock_requests_success):
        with patch(f"{Router.__module__}.docker", mock_docker),\
                patch(f"{ApplicationContainers.__module__}.docker", mock_docker),\
                patch(f"{Router.__module__}.requests", mock_requests_success):
            yield Router(config=route_config).app.test_client()

    def test_routing_success(self, router):
        response = router.get("/api/orders")
        assert response.status_code == 200

    def test_routing_failure(self, router):
        response = router.get("/api/cart")
        assert response.status_code == 403

    def test_routing_request_failure(self, router, mock_requests_failure):
        with patch(f"{Router.__module__}.requests", mock_requests_failure):
            response = router.get("/api/orders")
            assert response.status_code == 503

    def test_routing_stats(self, router):
        router.get("/api/orders")
        router.get("/api/payment")
        router.get("/api/orders")
        router.get("/api/payment")
        router.get("/api/cart")
        response = router.get("/stats")
        assert response.status_code == 200
        routing_stats = json.loads(response.data.decode())
        assert routing_stats["requests_count"] == {"error": 1, "success": 4}
        assert isinstance(routing_stats["latency_ms"]["average"], float)
        assert isinstance(routing_stats["latency_ms"]["p95"], float)
        assert isinstance(routing_stats["latency_ms"]["p99"], float)
