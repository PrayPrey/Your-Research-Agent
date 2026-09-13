"""Build partial domain lookup for PoC (first 3M docs from The Pile)."""
import sys
import logging
import pickle
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout),
                               logging.FileHandler("build_lookup.log")])

CACHE_PATH = Path("data/doc_to_domain_partial.pkl")
MAX_DOCS = 3_000_000  # 3M docs covers ~shard 0 content

if CACHE_PATH.exists():
    logging.info(f"Cache already exists at {CACHE_PATH}, skipping build.")
    sys.exit(0)

CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

from datasets import load_dataset

logging.info(f"Streaming EleutherAI/pile (first {MAX_DOCS:,} docs)...")
dataset = load_dataset("monology/pile-uncopyrighted", split="train", streaming=True)

doc_to_domain = {}
domain_counts = {}

for doc_idx, example in enumerate(tqdm(dataset, desc="Building domain lookup", total=MAX_DOCS)):
    domain = example["meta"]["pile_set_name"]
    doc_to_domain[doc_idx] = domain
    domain_counts[domain] = domain_counts.get(domain, 0) + 1
    if doc_idx + 1 >= MAX_DOCS:
        break

logging.info(f"Built lookup: {len(doc_to_domain):,} docs")
logging.info(f"Domain distribution: {dict(sorted(domain_counts.items(), key=lambda x: -x[1])[:10])}")

with open(CACHE_PATH, "wb") as f:
    pickle.dump(doc_to_domain, f, protocol=pickle.HIGHEST_PROTOCOL)

logging.info(f"Saved to {CACHE_PATH}")
print("LOOKUP BUILD COMPLETE")
