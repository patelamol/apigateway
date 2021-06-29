from datetime import datetime
from typing import Optional, Dict, Any
import numpy as np

from flask import Response, request


class RoutingStatistics:
    def __init__(self):
        self._success_counts: int = 0
        self._failre_counts: int = 0
        self._start_timestamp: Optional[datetime] = None
        self._execution_ms: np.ndarray = []

    @property
    def stats(self) -> Dict[str, Any]:
        execution_ms_np = np.array(self._execution_ms)
        return {
            "requests_count": {
                "success": self._success_counts,
                "error": self._failre_counts,
            },
            "latency_ms": {
                "average": np.mean(execution_ms_np),
                "p95": np.percentile(execution_ms_np, 95),
                "p99": np.percentile(execution_ms_np, 99),
            }
        }

    def log(self, response: Response) -> None:
        if 200 <= int(response.status_code) <= 399:
            self._success_counts += 1
        else:
            self._failre_counts += 1

    def start_timer(self):
        if request.path != "/favicon.ico":
            self._start_timestamp = datetime.now()

    def stop_timer(self):
        end_time = datetime.now()
        execution_micro_secs = (end_time - self._start_timestamp).microseconds / 1000
        print(f"execution_micro_secs: {execution_micro_secs}")
        self._execution_ms.append(execution_micro_secs)
        print(f"_execution_ms: {self._execution_ms}")
