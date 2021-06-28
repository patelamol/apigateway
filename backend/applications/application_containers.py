from typing import Optional, List, Dict

import docker
from docker import client as dockerclient


class ApplicationContainers:
    def __init__(self, docker_client: Optional[dockerclient] = None):
        self.docker_client = docker_client or docker.from_env()

    @property
    def docker_low_api_client(self):
        return docker.APIClient(base_url='unix://var/run/docker.sock')

    def get_app_container_by_labels(self, container_labels: List[Dict[str, str]]):
        labels = [f"{label['key']}={label['value']}" for label in container_labels]
        return self.docker_client.containers.list(filters={"label": labels})

    def get_container_endpoint(self, docker_id: str) -> Optional[str]:
        port_data = self.docker_low_api_client.inspect_container(docker_id)['NetworkSettings']['Ports']
        for host_port_maps in port_data.values():
            for host_port in host_port_maps:
                if host_port.get("HostIp"):
                    return host_port["HostIp"] + ":" + host_port["HostPort"]
        return None
