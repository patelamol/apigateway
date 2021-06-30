import pytest
from flask import Response

from apigateway.route.route_config import RouteConfig
from apigateway.route.utils import Route, ApplicationIdentifiers


class TestRouteConfig:
    @pytest.fixture
    def routes(self):
        return [
            Route(path_prefix="/api/orders", backend="orders"),
            Route(path_prefix="/api/payment", backend="payment"),
        ]

    @pytest.fixture
    def invalid_routes(self):
        return [
            Route(path_prefix="/api/cart", backend="cart"),
        ]

    @pytest.fixture
    def orders_app_identifier(self):
        return ApplicationIdentifiers(
            name="orders",
            matched_labels=["app_name=orders", "env=production"]
        )

    @pytest.fixture
    def payment_app_identifier(self):
        return ApplicationIdentifiers(
                name="payment",
                matched_labels=["app_name=payment", "env=production"]
            )

    @pytest.fixture
    def default_response(self):
        return Response(
            response="This is not reachable",
            status=403
        )

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

    def test_route_config(self, routes, orders_app_identifier, payment_app_identifier, default_response):
        route_config = RouteConfig(
            routes=routes,
            app_identifiers=[orders_app_identifier, payment_app_identifier],
            default_response=default_response
        )
        assert route_config.routes == {
            "/api/orders": orders_app_identifier,
            "/api/payment": payment_app_identifier
        }

    def test_route_config_invalid_routes(self, invalid_routes, orders_app_identifier, payment_app_identifier, default_response):
        with pytest.raises(ValueError) as exc_info:
            RouteConfig(
                routes=invalid_routes,
                app_identifiers=[orders_app_identifier, payment_app_identifier],
                default_response=default_response
            )
        assert str(exc_info.value) == "Route cart doesn't have corresponding application in app_identifiers"

    def test_parse(self, config_dict, orders_app_identifier, payment_app_identifier):
        route_config = RouteConfig.parse(config_dict)
        assert route_config.routes == {
            "/api/orders": orders_app_identifier,
            "/api/payment": payment_app_identifier
        }
