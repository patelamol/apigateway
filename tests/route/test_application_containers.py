from unittest.mock import patch, MagicMock
import docker

import pytest

from apigateway.route.application_containers import ApplicationContainers


class TestApplicationContainers:
    @pytest.fixture
    def mock_docker(self):
        mock_docker = MagicMock(spec=docker)
        mock_docker.from_env.return_value.containers.list.return_value = ["container_1"]
        mock_docker.APIClient.return_value.inspect_container.return_value = {
            "NetworkSettings": {
                "Ports": {"80tcp": [{"HostIp": "0.0.0.0", "HostPort": "8080"}]}
            }
        }
        return mock_docker

    @pytest.fixture
    def application_containers(self, mock_docker):
        with patch(f"{ApplicationContainers.__module__}.docker", mock_docker):
            yield ApplicationContainers()

    def test_get_app_container_by_labels(self, mock_docker, application_containers):
        labels = [
            {"key": "test", "value": "application-containers"}
        ]
        assert application_containers.get_app_container_by_labels(labels) == ["container_1"]
        mock_docker.from_env.assert_called()
        mock_docker.from_env.return_value.containers.list.assert_called_with(
            filters={"label": ["test=application-containers"]}
        )

    def test_get_container_endpoint(self, mock_docker, application_containers):
        assert application_containers.get_container_endpoint("docker-id") == "http://0.0.0.0:8080"
        mock_docker.APIClient.assert_called_with(base_url='unix://var/run/docker.sock')
