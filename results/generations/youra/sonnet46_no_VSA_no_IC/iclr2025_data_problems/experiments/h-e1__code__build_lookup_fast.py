"""Build partial domain lookup: 600K docs for PoC (covers checkpoints 0-586)."""
import sys
import logging
import pickle
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout),
                               logging.FileHandler("build_lookup_fast.log")])

# 600K docs covers step 0-586 (step_to_sample(586) = 586*2097152//2049 = 599_958)
CACHE_PATH = Path("data/doc_to_domain_partial.pkl")
MAX_DOCS = 600_000

if CACHE_PATH.exists():
    import pickle
    with open(CACHE_PATH, 'rb') as f:
        d = pickle.load(f)
    if len(d) >= MAX_DOCS:
        logging.info(f"Cache already has {len(d):,} docs >= {MAX_DOCS:,}. Skipping.")
        sys.exit(0)

CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

from datasets import load_dataset

logging.info(f"Streaming monology/pile-uncopyrighted (first {MAX_DOCS:,} docs)...")
dataset = load_dataset("monology/pile-uncopyrighted", split="train", streaming=True)

doc_to_domain = {}
domain_counts = {}

for doc_idx, example in enumerate(tqdm(dataset, desc="Building lookup", total=MAX_DOCS)):
    domain = example["meta"]["pile_set_name"]
    doc_to_domain[doc_idx] = domain
    domain_counts[domain] = domain_counts.get(domain, 0) + 1
    if doc_idx + 1 >= MAX_DOCS:
        break

logging.info(f"Built lookup: {len(doc_to_domain):,} docs")
logging.info(f"Domains found: {len(domain_counts)}")
logging.info(f"Top domains: {dict(sorted(domain_counts.items(), key=lambda x: -x[1])[:10])}")

with open(CACHE_PATH, "wb") as f:
    pickle.dump(doc_to_domain, f, protocol=pickle.HIGHEST_PROTOCOL)

logging.info(f"Saved to {CACHE_PATH}")
print("LOOKUP BUILD COMPLETE")
