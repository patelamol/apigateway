import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import numpy as np

from flask import Response, request


class RoutingStatistics:
    def __init__(self):
        self._success_counts: int = 0
        self._failre_counts: int = 0
        self._start_timestamp: Optional[datetime] = None
        self._execution_ms: List[float] = []
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel("DEBUG")

    @property
    def stats(self) -> Dict[str, Any]:
        execution_ms_np = np.array(self._execution_ms)
        average = None
        p95 = None
        p99 = None
        try:
            p95 = np.percentile(execution_ms_np, 95)
            p99 = np.percentile(execution_ms_np, 99)
            average = np.mean(execution_ms_np)
        except IndexError:
            self.logger.debug("No stats collected empty _execution_ms")
        return {
            "requests_count": {
                "success": self._success_counts,
                "error": self._failre_counts,
            },
            "latency_ms": {
                "average": average,
                "p95": p95,
                "p99": p99,
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
        self.logger.debug(f"execution_micro_secs: {execution_micro_secs}")
        self._execution_ms.append(execution_micro_secs)
        self.logger.debug(f"_execution_ms: {self._execution_ms}")
