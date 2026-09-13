"""Build LLM Leaderboard v1 CSV from open-llm-leaderboard-old/results HF dataset.

Downloads per-model JSON result files and extracts TruthfulQA MC2 + MMLU scores.
Saves to data/llm_leaderboard_v1/llm.csv
"""
import os
import json
import time
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("HUGGINGFACE_TOKEN") or os.environ.get("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
BASE_URL = "https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/main"
CACHE_DIR = "./data/llm_leaderboard_v1"
OUT_CSV = os.path.join(CACHE_DIR, "llm.csv")
PROPRIETARY = ["gpt", "claude", "gemini", "palm", "bard", "grok", "cohere/command"]


def get_file_list():
    """Get list of all result JSON files."""
    url = "https://huggingface.co/api/datasets/open-llm-leaderboard-old/results"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    sibs = r.json().get("siblings", [])
    return [s["rfilename"] for s in sibs if s["rfilename"].endswith(".json")]


def is_open_weight(model_name: str) -> bool:
    ml = model_name.lower()
    return not any(p in ml for p in PROPRIETARY)


def extract_scores(data: dict, model_name: str) -> dict | None:
    """Extract TruthfulQA MC2 and MMLU from result JSON."""
    results = data.get("results", {})

    truthfulqa = None
    mmlu = None

    for key, val in results.items():
        kl = key.lower()
        if "truthfulqa" in kl or "truthful_qa" in kl:
            # Look for mc2 metric
            if isinstance(val, dict):
                for mk, mv in val.items():
                    if "mc2" in mk.lower() and isinstance(mv, (int, float)):
                        truthfulqa = float(mv) * 100  # convert 0-1 to 0-100
                        break
                    if "acc" in mk.lower() and truthfulqa is None and isinstance(mv, (int, float)):
                        truthfulqa = float(mv) * 100

        if "mmlu" in kl and "harness" not in kl:
            if isinstance(val, dict):
                for mk, mv in val.items():
                    if "acc" in mk.lower() and isinstance(mv, (int, float)):
                        if mmlu is None:
                            mmlu = float(mv) * 100
                        break

    # Some JSONs store results with harness prefix
    if truthfulqa is None or mmlu is None:
        for key, val in results.items():
            kl = key.lower()
            if truthfulqa is None and ("truthful" in kl):
                if isinstance(val, dict):
                    for mk, mv in val.items():
                        if isinstance(mv, (int, float)):
                            truthfulqa = float(mv)
                            if truthfulqa <= 1.0:
                                truthfulqa *= 100
                            break
            if mmlu is None and "mmlu" in kl:
                if isinstance(val, dict):
                    for mk, mv in val.items():
                        if isinstance(mv, (int, float)):
                            mmlu = float(mv)
                            if mmlu <= 1.0:
                                mmlu *= 100
                            break

    if truthfulqa is not None and mmlu is not None:
        return {
            "model_name": model_name,
            "TruthfulQA_MC2": round(truthfulqa, 2),
            "MMLU": round(mmlu, 2),
        }
    return None


def fetch_file(fname: str, session: requests.Session) -> dict | None:
    """Fetch and parse one result JSON file."""
    # Infer model name from path: author/model-name/results_*.json
    parts = fname.split("/")
    if len(parts) < 3:
        return None
    model_name = "/".join(parts[:-1])  # e.g. mistralai/Mistral-7B-v0.1

    if not is_open_weight(model_name):
        return None

    url = f"{BASE_URL}/{fname}"
    try:
        r = session.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 429:
            time.sleep(5)
            r = session.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return None
        data = r.json()
        return extract_scores(data, model_name)
    except Exception:
        return None


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(OUT_CSV):
        df = pd.read_csv(OUT_CSV)
        print(f"Cache exists: {len(df)} models — skipping download")
        print(df.head())
        return df

    print("Fetching file list...")
    all_files = get_file_list()
    print(f"Total files: {len(all_files)}")

    # Strategy: take one file per unique model (earliest timestamp)
    model_to_file = {}
    for f in all_files:
        parts = f.split("/")
        if len(parts) < 3:
            continue
        model_name = "/".join(parts[:-1])
        if model_name not in model_to_file:
            model_to_file[model_name] = f  # first occurrence = earliest

    unique_files = list(model_to_file.values())
    print(f"Unique models: {len(unique_files)}")

    # Filter out known proprietary before downloading
    unique_files = [f for f in unique_files if is_open_weight("/".join(f.split("/")[:-1]))]
    print(f"Open-weight candidates: {len(unique_files)}")

    records = []
    session = requests.Session()

    # Sequential with rate limiting to avoid 429
    for i, fname in enumerate(unique_files):
        result = fetch_file(fname, session)
        if result:
            records.append(result)
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{len(unique_files)}, extracted={len(records)}")
            time.sleep(1)  # brief pause every 50 requests

    df = pd.DataFrame(records).drop_duplicates("model_name")
    df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved {len(df)} models to {OUT_CSV}")
    print(df.describe())
    return df


if __name__ == "__main__":
    main()
