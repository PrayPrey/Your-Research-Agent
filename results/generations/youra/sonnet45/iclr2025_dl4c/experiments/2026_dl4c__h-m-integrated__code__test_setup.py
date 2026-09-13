"""
Quick setup validation test
"""

import sys
import torch
from data_loader import HumanEvalPlusLoader

print("=" * 60)
print("H-E1 Setup Validation")
print("=" * 60)

# Check CUDA
print(f"\n[1/3] CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# Check dataset loading
print(f"\n[2/3] Testing dataset loading...")
loader = HumanEvalPlusLoader()
tasks = loader.load_dataset()
print(f"Successfully loaded {len(tasks)} tasks")

# Sample a task
sample_task = list(tasks.values())[0]
print(f"\nSample task: {sample_task['task_id']}")
print(f"Prompt length: {len(sample_task['prompt'])} chars")
print(f"Has tests: {len(sample_task['test']) > 0}")

print(f"\n[3/3] All checks passed!")
print("=" * 60)
