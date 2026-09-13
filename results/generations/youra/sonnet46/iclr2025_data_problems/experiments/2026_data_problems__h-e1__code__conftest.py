"""pytest configuration: add code directory to sys.path."""
import sys
import os

# Add the code directory itself to sys.path so test modules can import
# config, corpus_filter, etc. directly without package prefix.
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)
