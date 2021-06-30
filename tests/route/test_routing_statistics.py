import time
from unittest.mock import patch, MagicMock
import pytest
from datetime import datetime

from apigateway.route.routing_statistics import RoutingStatistics
from flask import Response


class TestRoutingStatistics:
    @pytest.fixture
    def success_response(self):
        return Response(response="Success", status=200)

    @pytest.fixture
    def failure_response(self):
        return Response(response="Forbidden", status=403)

    @pytest.fixture
    def mock_request(self):
        mock_request = MagicMock()
        mock_request.path = "/"
        return mock_request

    @pytest.fixture
    def stats_generator(self, mock_request):
        with patch(f"{RoutingStatistics.__module__}.request", mock_request):
            yield RoutingStatistics()

    def test_log_success(self, stats_generator, success_response):
        assert stats_generator._success_counts == 0
        assert stats_generator._failre_counts == 0
        stats_generator.log(success_response)
        assert stats_generator._success_counts == 1
        assert stats_generator._failre_counts == 0

    def test_log_failure(self, stats_generator, failure_response):
        assert stats_generator._success_counts == 0
        assert stats_generator._failre_counts == 0
        stats_generator.log(failure_response)
        assert stats_generator._failre_counts == 1
        assert stats_generator._success_counts == 0

    def test_start_timer(self, stats_generator):
        assert stats_generator._start_timestamp is None
        stats_generator.start_timer()
        assert isinstance(stats_generator._start_timestamp, datetime)

    def test_stop_timer(self, stats_generator):
        assert stats_generator._start_timestamp is None
        assert stats_generator._execution_ms == []
        stats_generator.start_timer()
        time.sleep(2)
        stats_generator.stop_timer()
        assert isinstance(stats_generator._start_timestamp, datetime)
        assert stats_generator._execution_ms[0] >= 2

    def test_stats(self, stats_generator, success_response, failure_response):
        assert stats_generator.stats == {
            "latency_ms": {"average": None, "p95": None, "p99": None},
            "requests_count": {"error": 0, "success": 0}
        }
        stats_generator.start_timer()
        stats_generator.log(success_response)
        stats_generator.stop_timer()

        stats_generator.start_timer()
        stats_generator.log(success_response)
        stats_generator.stop_timer()

        stats_generator.start_timer()
        stats_generator.log(failure_response)
        stats_generator.stop_timer()
        assert stats_generator.stats["requests_count"] == {"error": 1, "success": 2}
        assert isinstance(stats_generator.stats["latency_ms"]["average"], float)
        assert isinstance(stats_generator.stats["latency_ms"]["p95"], float)
        assert isinstance(stats_generator.stats["latency_ms"]["p99"], float)
