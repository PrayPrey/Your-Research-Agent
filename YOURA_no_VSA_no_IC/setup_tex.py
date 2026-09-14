#!/usr/bin/env python3
"""
setup_tex.py

Install TinyTeX and common LaTeX packages needed for paper/report builds.

Usage:
  python setup_tex.py
  python setup_tex.py --packages latexmk xetex fontspec kotex
  python setup_tex.py --skip-install-tinytex
  python setup_tex.py --dry-run

Notes:
- requirements.txt cannot reliably install system TeX binaries or TeX Live .sty packages.
- This script installs TinyTeX using the official TinyTeX installer, then uses tlmgr
  to install LaTeX packages.
- On Linux/macOS, it installs TinyTeX under ~/.TinyTeX by default.
- On Windows, it uses the official TinyTeX PowerShell installer.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_TEX_PACKAGES = [
    # Build tools / engines
    "latexmk",
    "xetex",
    "luatex",
    "bibtex",

    # Common LaTeX packages
    "fontspec",
    "unicode-math",
    "amsmath",
    "amssymb",
    "mathtools",
    "geometry",
    "graphicx",
    "graphics",
    "xcolor",
    "hyperref",
    "url",
    "booktabs",
    "multirow",
    "array",
    "longtable",
    "caption",
    "subcaption",
    "float",
    "enumitem",
    "natbib",
    "biblatex",
    "csquotes",
    "microtype",

    # Common conference / paper style dependencies
    "titlesec",
    "fancyhdr",
    "lastpage",
    "etoolbox",
    "xstring",
    "oberdiek",
    "kvoptions",
    "iftex",
    "ifplatform",
    "pdftexcmds",

    # Korean / CJK support. Remove if not needed.
    "kotex",
    "cjk",
    "xecjk",
    "collection-langenglish",
    "collection-langcjk",

    # Recommended broad bundles. These reduce missing .sty errors.
    "collection-latexrecommended",
    "collection-latexextra",
    "collection-fontsrecommended",
]


def run(cmd: list[str], *, env: dict[str, str] | None = None, dry_run: bool = False) -> None:
    print("+", " ".join(cmd))
    if dry_run:
        return
    subprocess.run(cmd, check=True, env=env)


def which(name: str) -> str | None:
    return shutil.which(name)


def detect_tlmgr() -> str | None:
    candidates = [
        which("tlmgr"),
        str(Path.home() / ".TinyTeX" / "bin" / "x86_64-linux" / "tlmgr"),
        str(Path.home() / ".TinyTeX" / "bin" / "universal-darwin" / "tlmgr"),
        str(Path.home() / "AppData" / "Roaming" / "TinyTeX" / "bin" / "windows" / "tlmgr.bat"),
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    return None


def tinytex_bin_dirs() -> list[Path]:
    home = Path.home()
    dirs = [
        home / ".TinyTeX" / "bin" / "x86_64-linux",
        home / ".TinyTeX" / "bin" / "aarch64-linux",
        home / ".TinyTeX" / "bin" / "universal-darwin",
        home / "AppData" / "Roaming" / "TinyTeX" / "bin" / "windows",
    ]
    return [d for d in dirs if d.exists()]


def tex_env() -> dict[str, str]:
    env = os.environ.copy()
    bin_dirs = tinytex_bin_dirs()
    if bin_dirs:
        env["PATH"] = os.pathsep.join(str(d) for d in bin_dirs) + os.pathsep + env.get("PATH", "")
    return env


def install_tinytex(dry_run: bool = False) -> None:
    system = platform.system().lower()

    if detect_tlmgr():
        print("TinyTeX/TeX Live already appears to be installed.")
        return

    if system in {"linux", "darwin"}:
        downloader = which("curl") or which("wget")
        if not downloader:
            raise RuntimeError("curl or wget is required to install TinyTeX.")

        if which("curl"):
            cmd = [
                "sh",
                "-c",
                "curl -L https://yihui.org/tinytex/install-bin-unix.sh | sh",
            ]
        else:
            cmd = [
                "sh",
                "-c",
                "wget -qO- https://yihui.org/tinytex/install-bin-unix.sh | sh",
            ]
        run(cmd, dry_run=dry_run)
        return

    if system == "windows":
        if not which("powershell") and not which("pwsh"):
            raise RuntimeError("PowerShell is required to install TinyTeX on Windows.")
        ps = which("pwsh") or which("powershell")
        assert ps is not None
        cmd = [
            ps,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            "iwr -useb https://yihui.org/tinytex/install-bin-windows.ps1 | iex",
        ]
        run(cmd, dry_run=dry_run)
        return

    raise RuntimeError(f"Unsupported OS: {platform.system()}")


def install_tex_packages(packages: list[str], dry_run: bool = False) -> None:
    env = tex_env()
    tlmgr = detect_tlmgr() or which("tlmgr")
    if not tlmgr:
        raise RuntimeError("tlmgr was not found. Install TinyTeX first or add tlmgr to PATH.")

    # Make tlmgr itself reasonably current, but do not fail the whole setup if update
    # is blocked by a TeX Live repository/version mismatch.
    try:
        run([tlmgr, "update", "--self"], env=env, dry_run=dry_run)
    except subprocess.CalledProcessError:
        print("Warning: tlmgr self-update failed. Continuing with package installation...")

    for pkg in packages:
        try:
            run([tlmgr, "install", pkg], env=env, dry_run=dry_run)
        except subprocess.CalledProcessError:
            print(f"Warning: failed to install TeX package: {pkg}")


def verify() -> None:
    env = tex_env()
    checks = ["tlmgr", "latexmk", "pdflatex", "xelatex", "lualatex", "bibtex"]
    print("\nVerification:")
    for exe in checks:
        path = shutil.which(exe, path=env.get("PATH"))
        print(f"  {exe}: {path or 'NOT FOUND'}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--packages",
        nargs="*",
        default=DEFAULT_TEX_PACKAGES,
        help="TeX Live package names to install with tlmgr.",
    )
    parser.add_argument(
        "--skip-install-tinytex",
        action="store_true",
        help="Do not install TinyTeX; only install packages with existing tlmgr.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them.",
    )
    args = parser.parse_args()

    try:
        if not args.skip_install_tinytex:
            install_tinytex(dry_run=args.dry_run)

        install_tex_packages(args.packages, dry_run=args.dry_run)
        verify()

        print("\nDone.")
        print("If commands are still not found, restart your shell or add TinyTeX's bin directory to PATH.")
        return 0
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
