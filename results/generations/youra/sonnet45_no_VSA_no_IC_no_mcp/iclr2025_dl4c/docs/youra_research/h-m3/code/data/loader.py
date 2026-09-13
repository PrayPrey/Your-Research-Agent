"""Dataset loading for HumanEval and MBPP."""
from typing import List, Dict, Any
from dataclasses import dataclass
from datasets import load_dataset
import os

@dataclass
class Problem:
    """Single problem instance."""
    id: str
    prompt: str
    tests: List[str]
    dataset: str

def load_humaneval(n_samples: int = 100) -> List[Problem]:
    """Load HumanEval problems. Returns first n_samples."""
    os.environ['HF_DATASETS_CACHE'] = '/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/.data_cache/datasets'

    ds = load_dataset("openai_humaneval", split="test")
    problems = []

    for i, item in enumerate(ds):
        if i >= n_samples:
            break

        problems.append(Problem(
            id=item["task_id"],
            prompt=item["prompt"],
            tests=[item["test"]],  # HumanEval has one test field
            dataset="humaneval"
        ))

    return problems

def load_mbpp(n_samples: int = 100, seed: int = 42) -> List[Problem]:
    """Load MBPP problems. Random sample n_samples."""
    os.environ['HF_DATASETS_CACHE'] = '/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/.data_cache/datasets'

    ds = load_dataset("mbpp", split="test")
    ds = ds.shuffle(seed=seed).select(range(min(n_samples, len(ds))))

    problems = []
    for item in ds:
        problems.append(Problem(
            id=str(item["task_id"]),
            prompt=item["text"],
            tests=item["test_list"],
            dataset="mbpp"
        ))

    return problems

def load_all_datasets(n_samples: int = 100) -> Dict[str, List[Problem]]:
    """Load all datasets. Returns dict keyed by dataset name."""
    return {
        "humaneval": load_humaneval(n_samples),
        "mbpp": load_mbpp(n_samples, seed=42)
    }
