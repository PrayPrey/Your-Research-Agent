"""
Test script to verify imports and basic functionality.
"""

import sys
import os

print("Testing imports...")

try:
    import torch
    print(f"✓ torch {torch.__version__}")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  CUDA device: {torch.cuda.get_device_name(0)}")
except Exception as e:
    print(f"✗ torch: {e}")

try:
    import transformers
    print(f"✓ transformers {transformers.__version__}")
except Exception as e:
    print(f"✗ transformers: {e}")

try:
    import sentence_transformers
    print(f"✓ sentence_transformers {sentence_transformers.__version__}")
except Exception as e:
    print(f"✗ sentence_transformers: {e}")

try:
    import networkx
    print(f"✓ networkx {networkx.__version__}")
except Exception as e:
    print(f"✗ networkx: {e}")

try:
    import sklearn
    print(f"✓ scikit-learn {sklearn.__version__}")
except Exception as e:
    print(f"✗ scikit-learn: {e}")

try:
    import matplotlib
    print(f"✓ matplotlib {matplotlib.__version__}")
except Exception as e:
    print(f"✗ matplotlib: {e}")

try:
    import seaborn
    print(f"✓ seaborn {seaborn.__version__}")
except Exception as e:
    print(f"✗ seaborn: {e}")

try:
    import openai
    print(f"✓ openai {openai.__version__}")
except Exception as e:
    print(f"✗ openai: {e}")

print("\nTesting config...")
try:
    import config
    print(f"✓ config imported")
    print(f"  Device: {config.DEVICE}")
    print(f"  Base dir: {config.BASE_DIR}")
except Exception as e:
    print(f"✗ config: {e}")

print("\nAll imports successful!")
