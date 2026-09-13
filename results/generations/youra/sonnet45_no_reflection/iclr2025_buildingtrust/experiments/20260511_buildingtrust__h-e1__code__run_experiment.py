#!/usr/bin/env python
"""Entry point for H-E1 experiment"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import main

if __name__ == "__main__":
    main()
