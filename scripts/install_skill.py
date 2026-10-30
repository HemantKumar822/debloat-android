#!/usr/bin/env python3
"""Install the reviewed local Debloat Android source; does not download or execute code."""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(ROOT))
from android_care.installation import PROJECT_DIRS, install, installation_target


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(errors='backslashreplace')
    parser = argparse.ArgumentParser(description='Install Debloat Android as the android-device-care skill.')
    parser.add_argument('--agent', required=True, choices=PROJECT_DIRS)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument('--project', type=Path, help='Project directory (created if needed)')
    scope.add_argument('--user', action='store_true', help='Install for the current user')
    parser.add_argument('--dry-run', action='store_true', help='Validate and list files without writing')
    args = parser.parse_args(argv)
    try:
        target = installation_target(args.agent, project=args.project, user=args.user)
        files = install(ROOT, target, dry_run=args.dry_run)
    except (OSError, ValueError) as exc:
        print(f'Installation stopped: {exc}', file=sys.stderr)
        return 2
    print(f'{"Would install" if args.dry_run else "Installed"} {len(files)} files: {target}')
    if args.dry_run:
        print('\n'.join(files))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
