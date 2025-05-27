from __future__ import annotations

import argparse
import os
import sys
from logging.config import dictConfig

import greqs
from greqs.helper import file_template

current_dir = os.getcwd()
sys.path.insert(0, current_dir)

parser = argparse.ArgumentParser(
    __package__, description="Get requirements from modules (or packages)"
)
parser.add_argument("module", type=str, nargs="+")
parser.add_argument("--verbose", action="store_true", help="enable verbose mode")
parser.add_argument(
    "--output",
    type=str,
    help="output the requirements to a file",
    metavar="FILE",
)
parser.add_argument(
    "--version", action="version", version="%(prog)s {0}".format(greqs.__version__)
)


def main(argv: list[str] | None = None):
    args = parser.parse_args(argv)
    if args.verbose:
        dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": "%(message)s",
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "stream": sys.stderr,
                        "formatter": "default",
                    }
                },
                "root": {"level": "DEBUG", "handlers": ["console"]},
            }
        )

    content = os.linesep.join(greqs.main(args.module))
    if args.output is not None:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(file_template(content))
    else:
        print(content)
