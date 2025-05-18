import argparse
import os
import sys
from logging.config import dictConfig

current_dir = os.getcwd()
sys.path.insert(0, current_dir)

parser = argparse.ArgumentParser(__package__)
parser.add_argument("module", type=str, nargs=1)
parser.add_argument("--verbose", action="store_true")


def main():
    import greqs

    args = parser.parse_args()
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

    for i in greqs.main(args.module[0]):
        print(i)
