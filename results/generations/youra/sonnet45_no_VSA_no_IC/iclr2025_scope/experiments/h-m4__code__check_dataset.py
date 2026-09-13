"""Check LongBench multi-doc QA tasks"""
from datasets import load_dataset

# LongBench tasks - identify multi-doc QA
longbench_tasks = [
    "hotpotqa",  # Multi-hop QA
    "2wikimqa",  # Multi-hop QA
    "musique",   # Multi-hop QA
    "multifieldqa_en",  # Multi-field QA
]

for task in longbench_tasks:
    try:
        ds = load_dataset('THUDM/LongBench', task, split='test')
        print(f"\n{task}:")
        print(f"  Samples: {len(ds)}")
        if len(ds) > 0:
            sample = ds[0]
            print(f"  Keys: {list(sample.keys())}")
            print(f"  Context length: {len(sample.get('context', '').split())}")
    except Exception as e:
        print(f"\n{task}: ERROR - {e}")
