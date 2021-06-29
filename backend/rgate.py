import argparse
import sys
from pathlib import Path

import yaml

from backend.route.route_config import RouteConfig
from backend.route.router import Router


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rgate",
        description="rgate.",
    )
    parser.add_argument(
        "--config",
        dest="config",
        type=str,
        default="example/test_payload.yml",
        help="Relative path to current working directory for routing config yaml"
    )
    return parser


def main():
    arg_parser = get_parser()
    namespace = arg_parser.parse_args(sys.argv[1:])
    test_file_path = Path.cwd() / namespace.config
    config_dict = yaml.load(test_file_path.read_text())
    route_config = RouteConfig.parse(config_dict)
    router = Router(route_config)
    router.run()


if __name__ == '__main__':
    main()
