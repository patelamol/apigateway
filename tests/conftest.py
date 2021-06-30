import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def backend_docker_compose_file():
    return Path("example/test_payload.yml")


@pytest.fixture
def backend_containers(backend_docker_compose_file):
    process = subprocess.Popen(
        ["docker-compose", "-f", backend_docker_compose_file.as_posix(), "up", "-d"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    yield
    subprocess.run(["docker", "container", "stop", "$(docker ps -a -q --filter=label=test=application-containers)"])


