from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Route:
    path_prefix: str
    backend: str


@dataclass
class ApplicationIdentifiers:
    name: str
    matched_labels: list[str]
    _labels: list[Dict[str, str]] = field(default_factory=list)

    def __post_init__(self):
        self._labels = [
            {"key": l.split("=")[0], "value": l.split("=")[1]} for l in self.matched_labels
        ]

    @property
    def labels(self) -> list[Dict[str, str]]:
        return self._labels

    def as_dict(self):
        return {
            "name": self.name,
            "labels": self._labels
        }
