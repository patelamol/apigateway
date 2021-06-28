from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Route:
    path_prefix: str
    backend: str


class ApplicationIdentifiers:
    def __init__(self, name: str):
        self.name = name
        self._labels: list[Dict[str, str]] = []

    @property
    def labels(self) -> list[Dict[str, str]]:
        return self._labels

    def add_label(self, key: str, value: str):
        self._labels.append({"key": key, "value": value})