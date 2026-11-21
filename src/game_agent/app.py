"""Command-line entry point for the local agent foundation."""

import argparse
import json
from pathlib import Path

from .config import load_config
from .health import check_health
from .logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Autonomous PC game agent")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="optional YAML configuration path",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health", help="run local foundation health checks")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    configure_logging(config.logging.level)
    if args.command == "health":
        print(json.dumps(check_health().as_dict(), sort_keys=True))
        return 0
    return 2
