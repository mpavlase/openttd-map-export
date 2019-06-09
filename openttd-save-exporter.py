#!/usr/bin/env python3

import argparse
from openttdexport import TTDMap


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="Plain text export of saved game")
    parser.add_argument('output', help="Filename of output picture in PNG format")
    parser.add_argument('--size',
            type=int,
            default=3,
            help="'pixel' size")

    args = parser.parse_args()

    ttdmap = TTDMap(pixel_size=args.size)
    ttdmap.load_from_file(args.input)
    ttdmap.render(args.output)
