from dataclasses import dataclass, asdict
from typing import Dict, Any, List


@dataclass
class Route:
    path_prefix: str
    backend: str


class ApplicationIdentifiers:
    def __init__(self, name: str, labels: List[str]):
        self.name = name
        self.labels: list[Dict[str, str]] = [{"key": l.split("=")[0], "value": l.split("=")[1]} for l in labels]
