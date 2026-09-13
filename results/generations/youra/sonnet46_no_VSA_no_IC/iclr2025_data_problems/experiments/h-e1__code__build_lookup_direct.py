"""Build domain lookup by directly streaming JSONL.zst shard via HTTP.
Parses first 600K docs without loading the full HuggingFace dataset library.
"""
import sys
import logging
import pickle
import json
import io
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout),
                               logging.FileHandler("build_lookup_direct.log")])

CACHE_PATH = Path("data/doc_to_domain_partial.pkl")
MAX_DOCS = 600_000

if CACHE_PATH.exists():
    with open(CACHE_PATH, 'rb') as f:
        d = pickle.load(f)
    if len(d) >= MAX_DOCS:
        logging.info(f"Cache already has {len(d):,} docs. Skipping.")
        sys.exit(0)

CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Try to use the HuggingFace token if available
try:
    with open(Path.home() / ".cache/huggingface/token") as f:
        token = f.read().strip()
except Exception:
    token = None

# Direct URL to pile-uncopyrighted shard 00
# monology/pile-uncopyrighted train/00.jsonl.zst
HF_BASE = "https://huggingface.co/datasets/monology/pile-uncopyrighted/resolve/main"
SHARD_URL = f"{HF_BASE}/train/00.jsonl.zst"

logging.info(f"Downloading and streaming {SHARD_URL}...")
logging.info(f"Target: first {MAX_DOCS:,} docs")

try:
    import zstandard as zstd
    HAVE_ZSTD = True
except ImportError:
    HAVE_ZSTD = False
    logging.info("zstandard not found, installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "zstandard", "-q"], check=True)
    import zstandard as zstd

headers = {"User-Agent": "python/urllib"}
if token:
    headers["Authorization"] = f"Bearer {token}"

req = urllib.request.Request(SHARD_URL, headers=headers)

doc_to_domain = {}
domain_counts = {}
doc_idx = 0

with urllib.request.urlopen(req, timeout=60) as response:
    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(response) as reader:
        text_stream = io.TextIOWrapper(reader, encoding="utf-8")
        for line in text_stream:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                domain = obj.get("meta", {}).get("pile_set_name", "Unknown")
                doc_to_domain[doc_idx] = domain
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            except json.JSONDecodeError:
                pass
            doc_idx += 1

            if doc_idx % 50000 == 0:
                logging.info(f"  {doc_idx:,} docs processed...")

            if doc_idx >= MAX_DOCS:
                break

logging.info(f"Built lookup: {len(doc_to_domain):,} docs")
logging.info(f"Domains found: {len(domain_counts)}")
top10 = dict(sorted(domain_counts.items(), key=lambda x: -x[1])[:10])
logging.info(f"Top domains: {top10}")

with open(CACHE_PATH, "wb") as f:
    pickle.dump(doc_to_domain, f, protocol=pickle.HIGHEST_PROTOCOL)

logging.info(f"Saved to {CACHE_PATH}")
print("LOOKUP BUILD COMPLETE")
