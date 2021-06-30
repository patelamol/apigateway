from apigateway.route.utils import Route, ApplicationIdentifiers


class TestUtils:
    def test_route(self):
        path_prefix = "/api/orders"
        backend = "orders"
        route = Route(path_prefix, backend)
        assert route.path_prefix == path_prefix
        assert route.backend == backend

    def test_application_identifier(self):
        app_identifier = ApplicationIdentifiers(
            name="payment",
            matched_labels=["app_name=payment", "env=production"]
        )
        assert app_identifier.as_dict() == {
            "name": "payment",
            "labels": [
                {"key": "app_name", "value": "payment"},
                {"key": "env", "value": "production"},
            ]
        }

