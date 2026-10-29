#!/usr/bin/env python3
"""Entry point that works from any current working directory."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from android_care.cli import main
if __name__ == "__main__":
    raise SystemExit(main())
