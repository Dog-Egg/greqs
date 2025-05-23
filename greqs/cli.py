from __future__ import annotations

import argparse
import os
import sys
from logging.config import dictConfig

import greqs

current_dir = os.getcwd()
sys.path.insert(0, current_dir)

parser = argparse.ArgumentParser(__package__)
parser.add_argument("module", type=str, nargs=1)
parser.add_argument("--verbose", action="store_true")
parser.add_argument(
    "--output",
    type=str,
    help="output the requirements to the file",
    metavar="FILE",
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

    content = os.linesep.join(greqs.main(args.module[0]))
    if args.output is not None:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print(content)
