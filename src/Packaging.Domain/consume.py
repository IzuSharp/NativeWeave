#!/usr/bin/env python3
"""Run the manifest-driven database PackageReference consumer."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[2] / "tests/Packaging.Domain/consumer_cases.py"), run_name="__main__")
