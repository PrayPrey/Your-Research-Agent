#!/usr/bin/env python
"""Entry point for H-M4 experiment"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from main_h_m4_simple import main

if __name__ == "__main__":
    print("Starting H-M4: Cross-Architecture Directional Replication (PoC)")
    success = main()
    sys.exit(0 if success else 1)
