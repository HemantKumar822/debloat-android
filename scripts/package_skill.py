#!/usr/bin/env python3
"""Build the curated portable Debloat Android ZIP using the installer manifest."""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(ROOT))
from android_care.installation import package


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(errors='backslashreplace')
    parser = argparse.ArgumentParser(description='Build a portable Debloat Android skill ZIP.')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        files = package(ROOT, args.output)
    except (OSError, ValueError) as exc:
        print(f'Packaging stopped: {exc}', file=sys.stderr)
        return 2
    print(f'Packaged {len(files)} files: {args.output.absolute()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
