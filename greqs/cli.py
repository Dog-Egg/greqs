import argparse
import os
import sys

current_dir = os.getcwd()
sys.path.insert(0, current_dir)

parser = argparse.ArgumentParser(__package__)
parser.add_argument("module", type=str, nargs=1)


def main():
    import greqs

    args = parser.parse_args()
    for i in greqs.main(args.module[0]):
        print(i)
