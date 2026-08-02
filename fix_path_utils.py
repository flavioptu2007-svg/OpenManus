#!/usr/bin/env python3
"""
Shared utility for inject_*.py and fix_*.py scripts.
Provides configurable V3_PATH via argparse with backward-compatible defaults.
"""

import argparse
import os


# Default path (backward-compatible)
_DEFAULT_V3 = os.path.join(
    os.path.expanduser("~"), "Secretária", "Download", "planejador-escolar-v3.0.html"
)
_DEFAULT_OMREDU = os.path.join(
    os.path.expanduser("~"), "OpenManus", "omredu_corretor_gabaritos.html"
)

__all__ = ["add_v3_path_arg", "resolve_v3_path", "read_file", "write_file"]


def add_v3_path_arg(
    parser=None, description="Fix or inject into the Planejador v3.0 HTML file"
) -> argparse.ArgumentParser:
    """Add --v3-path and optional --omredu-path arguments to an argparse parser."""
    if parser is None:
        parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--v3-path",
        default=_DEFAULT_V3,
        help=f"Path to planejador-escolar-v3.0.html (default: {_DEFAULT_V3})",
    )
    return parser


def resolve_v3_path(args=None) -> str:
    """Parse args (if not provided) and return the resolved V3_PATH."""
    if args is None:
        parser = argparse.ArgumentParser(
            description="Fix or inject into the Planejador v3.0 HTML file"
        )
        parser.add_argument(
            "--v3-path",
            default=_DEFAULT_V3,
            help=f"Path to HTML file (default: {_DEFAULT_V3})",
        )
        args = parser.parse_args()
    return args.v3_path


def read_file(path):
    """Read a file with UTF-8 encoding."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    """Write content to a file with UTF-8 encoding."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
