import os
import pandas as pd
from dataset import load_all_problems
from completions import load_completions_jsonl
from eval_pass1 import evaluate_all
from metrics import build_dataframe
from config import CONFIG

def load_model_dataframe(model_id: str, problems: list, completions_path: str) -> pd.DataFrame:
    completions = load_completions_jsonl(completions_path)
    passed = evaluate_all(problems, completions)
    df = build_dataframe(problems, completions, passed)
    df["model_id"] = model_id
    return df

def build_multi_model_dataframe(models: list[str], problems: list, completions_dir: str) -> pd.DataFrame:
    import random
    dfs = []
    max_samples = getattr(CONFIG, 'max_samples_per_model', len(problems))
    if max_samples < len(problems):
        random.seed(CONFIG.seed)
        problems = random.sample(problems, max_samples)
        print(f"Sampled {max_samples} problems for efficiency")
    for m in models:
        path = f"{completions_dir}/{m}.jsonl"
        if not os.path.exists(path):
            print(f"Warning: Skipping {m}, no completions at {path}")
            continue
        print(f"Loading {m}...")
        df = load_model_dataframe(m, problems, path)
        print(f"  {m}: {len(df)} samples, pass_rate={df['passed'].mean():.2%}")
        dfs.append(df)
    if len(dfs) < CONFIG.min_models:
        raise ValueError(f"Need at least {CONFIG.min_models} models, got {len(dfs)}")
    combined = pd.concat(dfs, ignore_index=True)
    expected_cols = ["task_id", "model_id", "passed", "pylint_score", "mypy_errors", "radon_cc", "loc"]
    for col in expected_cols:
        assert col in combined.columns, f"Missing column: {col}"
    return combined
