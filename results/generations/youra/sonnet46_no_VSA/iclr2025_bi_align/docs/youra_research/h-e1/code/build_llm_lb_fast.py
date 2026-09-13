"""Fast LLM LB v1 builder: targeted fetch of known open-weight models.

Uses the file list already retrieved to pick representative open-weight models
and fetch their result JSONs efficiently.
"""
import os
import json
import time
import requests
import pandas as pd

TOKEN = os.environ.get("HUGGINGFACE_TOKEN") or os.environ.get("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
BASE_URL = "https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/main"
CACHE_DIR = "./data/llm_leaderboard_v1"
OUT_CSV = os.path.join(CACHE_DIR, "llm.csv")

PROPRIETARY = ["gpt-4", "gpt-3.5", "claude", "gemini", "palm", "bard", "grok",
               "openai", "anthropic", "google/bard"]

# Well-known open-weight models from the v1 leaderboard era
KNOWN_MODELS = {
    "mistralai/Mistral-7B-v0.1": "mistralai/Mistral-7B-v0.1/results_2023-09-27T15-30-59.039834.json",
    "meta-llama/Llama-2-7b-hf": "meta-llama/Llama-2-7b-hf/results_2023-08-20T17-54-59.197846.json",
    "meta-llama/Llama-2-13b-hf": "meta-llama/Llama-2-13b-hf/results_2023-08-20T17-57-59.197846.json",
    "meta-llama/Llama-2-70b-hf": "meta-llama/Llama-2-70b-hf/results_2023-08-20T18-00-00.000000.json",
    "tiiuae/falcon-7b": "tiiuae/falcon-7b/results_2023-09-01T00-00-00.000000.json",
    "EleutherAI/gpt-neox-20b": "EleutherAI/gpt-neox-20b/results_2023-07-01T00-00-00.000000.json",
    "bigscience/bloom": "bigscience/bloom/results_2023-07-01T00-00-00.000000.json",
    "mistralai/Mixtral-8x7B-v0.1": "mistralai/Mixtral-8x7B-v0.1/results_2024-01-01T00-00-00.000000.json",
}


def get_file_list():
    url = "https://huggingface.co/api/datasets/open-llm-leaderboard-old/results"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    sibs = r.json().get("siblings", [])
    return [s["rfilename"] for s in sibs if s["rfilename"].endswith(".json")]


def is_open_weight(model_name: str) -> bool:
    ml = model_name.lower()
    return not any(p in ml for p in PROPRIETARY)


def extract_scores(data: dict, model_name: str) -> dict | None:
    results = data.get("results", {})
    truthfulqa = None
    mmlu_scores = []

    for key, val in results.items():
        kl = key.lower()
        if not isinstance(val, dict):
            continue

        # TruthfulQA MC2
        if ("truthfulqa" in kl or "truthful" in kl) and truthfulqa is None:
            for mk, mv in val.items():
                if "mc2" in mk.lower() and isinstance(mv, (int, float)):
                    v = float(mv)
                    truthfulqa = v * 100 if v <= 1.0 else v
                    break
            if truthfulqa is None:
                for mk, mv in val.items():
                    if isinstance(mv, (int, float)):
                        v = float(mv)
                        truthfulqa = v * 100 if v <= 1.0 else v
                        break

        # MMLU (average across subjects)
        if "mmlu" in kl:
            for mk, mv in val.items():
                if "acc" in mk.lower() and isinstance(mv, (int, float)):
                    v = float(mv)
                    mmlu_scores.append(v * 100 if v <= 1.0 else v)
                    break

    mmlu = sum(mmlu_scores) / len(mmlu_scores) if mmlu_scores else None

    if truthfulqa is not None and mmlu is not None:
        return {
            "model_name": model_name,
            "TruthfulQA_MC2": round(truthfulqa, 2),
            "MMLU": round(mmlu, 2),
        }
    return None


def fetch_one(session, fname, model_name):
    url = f"{BASE_URL}/{fname}"
    for attempt in range(3):
        try:
            r = session.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 429:
                time.sleep(10 * (attempt + 1))
                continue
            if r.status_code == 200:
                return extract_scores(r.json(), model_name)
            return None
        except Exception:
            time.sleep(2)
    return None


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(OUT_CSV):
        df = pd.read_csv(OUT_CSV)
        print(f"Cache exists: {len(df)} models")
        print(df.to_string())
        return df

    print("Fetching complete file list...")
    all_files = get_file_list()
    print(f"Total files in dataset: {len(all_files)}")

    # Build model -> [files] mapping
    model_to_files = {}
    for f in all_files:
        parts = f.split("/")
        if len(parts) < 3:
            continue
        model_name = "/".join(parts[:-1])
        model_to_files.setdefault(model_name, []).append(f)

    open_weight_models = {m: files for m, files in model_to_files.items()
                          if is_open_weight(m)}
    print(f"Open-weight unique models: {len(open_weight_models)}")

    session = requests.Session()
    records = []
    count = 0
    total = len(open_weight_models)

    for model_name, files in open_weight_models.items():
        fname = files[0]  # first (earliest) file
        result = fetch_one(session, fname, model_name)
        if result:
            records.append(result)
        count += 1
        if count % 10 == 0:
            print(f"  {count}/{total} processed, {len(records)} with scores")
        if count % 100 == 0:
            time.sleep(2)

    df = pd.DataFrame(records).drop_duplicates("model_name")
    df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved {len(df)} models")
    print(df.describe())
    return df


if __name__ == "__main__":
    main()
