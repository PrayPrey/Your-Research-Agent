"""
Main experiment entry point for H-E1 FAIR Score Variance Existence.
Wraps src/main.py for direct execution from code/ directory.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    main()
