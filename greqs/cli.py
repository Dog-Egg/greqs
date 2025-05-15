import argparse

parser = argparse.ArgumentParser(__package__)
parser.add_argument("module", type=str, nargs=1)


def main():
    import greqs

    args = parser.parse_args()
    for i in greqs.main(args.module[0]):
        print(i)
