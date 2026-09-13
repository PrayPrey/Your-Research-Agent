"""Parallel fetch of LLM LB v1 data from open-llm-leaderboard-old/results.

Keys in result JSONs:
  TruthfulQA MC2: "harness|truthfulqa:mc|0" -> "mc2"
  MMLU: "harness|hendrycksTest-{subject}|5" -> "acc" (average across subjects)
"""
import os
import time
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("HUGGINGFACE_TOKEN") or os.environ.get("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
BASE_URL = "https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/main"
CACHE_DIR = "./data/llm_leaderboard_v1"
OUT_CSV = os.path.join(CACHE_DIR, "llm.csv")
MAX_MODELS = 500
MAX_WORKERS = 6
MIN_INTERVAL = 0.2

PROPRIETARY = ["gpt-4", "gpt-3.5", "openai/", "claude", "anthropic",
               "gemini", "palm", "bard", "grok", "cohere/command",
               "ai21", "titan", "command-r"]

_rate_lock = threading.Lock()
_last_req = [0.0]


def rate_get(session, url):
    with _rate_lock:
        elapsed = time.time() - _last_req[0]
        if elapsed < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - elapsed)
        _last_req[0] = time.time()
    for attempt in range(4):
        try:
            r = session.get(url, headers=HEADERS, timeout=25)
            if r.status_code == 429:
                time.sleep(20 * (attempt + 1))
                continue
            return r
        except Exception:
            time.sleep(3)
    return None


def is_open(name):
    nl = name.lower()
    return not any(p in nl for p in PROPRIETARY)


def extract(data, model_name):
    results = data.get("results", {})
    if not results:
        return None

    # TruthfulQA MC2
    tqa = None
    tqa_val = results.get("harness|truthfulqa:mc|0", {})
    if isinstance(tqa_val, dict):
        mc2 = tqa_val.get("mc2")
        if isinstance(mc2, (int, float)):
            v = float(mc2)
            tqa = v * 100 if v <= 1.0 else v

    # MMLU: average all hendrycksTest subjects
    mmlu_acc = []
    for k, v in results.items():
        if "hendrycksTest" in k and isinstance(v, dict):
            acc = v.get("acc")
            if isinstance(acc, (int, float)):
                f = float(acc)
                mmlu_acc.append(f * 100 if f <= 1.0 else f)

    if not mmlu_acc:
        return None
    mmlu = sum(mmlu_acc) / len(mmlu_acc)

    if tqa is None:
        return None

    return {
        "model_name": model_name,
        "TruthfulQA_MC2": round(tqa, 2),
        "MMLU": round(mmlu, 2),
    }


def fetch_one(session, fname, model_name):
    url = f"{BASE_URL}/{fname}"
    r = rate_get(session, url)
    if r is None or r.status_code != 200:
        return None
    try:
        return extract(r.json(), model_name)
    except Exception:
        return None


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)

    if os.path.exists(OUT_CSV):
        df = pd.read_csv(OUT_CSV)
        if len(df) > 0:
            print(f"Cache exists: {len(df)} models")
            print(df.describe())
            return df
        os.remove(OUT_CSV)

    print("Fetching file list...")
    s0 = requests.Session()
    r = rate_get(s0, "https://huggingface.co/api/datasets/open-llm-leaderboard-old/results")
    sibs = r.json().get("siblings", [])
    json_files = [s["rfilename"] for s in sibs if s["rfilename"].endswith(".json")]
    print(f"Total files: {len(json_files)}")

    model_to_file = {}
    for f in json_files:
        parts = f.split("/")
        if len(parts) < 3:
            continue
        mname = "/".join(parts[:-1])
        if mname not in model_to_file and is_open(mname):
            model_to_file[mname] = f

    candidates = list(model_to_file.items())[:MAX_MODELS]
    print(f"Open-weight candidates: {len(candidates)}")

    session = requests.Session()
    records = []
    done = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_one, session, fname, mname): mname
            for mname, fname in candidates
        }
        for fut in as_completed(futures):
            res = fut.result()
            done += 1
            if res:
                records.append(res)
            if done % 25 == 0:
                print(f"  {done}/{len(candidates)} done, {len(records)} scored")

    df = pd.DataFrame(records).drop_duplicates("model_name")
    df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved {len(df)} models to {OUT_CSV}")
    if len(df) > 0:
        print(df.describe())
    return df


if __name__ == "__main__":
    main()
