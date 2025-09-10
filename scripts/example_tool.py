#!/usr/bin/env python
"""
Example standalone script you can run with `python scripts/example_tool.py`.
Later, you can move logic into the package and expose via an entry point.
"""

import sys


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    name = argv[0] if argv else "world"
    print(f"Hello, {name}! This is example_tool.")


if __name__ == "__main__":
    main()
