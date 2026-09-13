"""Bibliometric client - uses arXiv API for paper counts.

Semantic Scholar and Google Scholar rate-limited. arXiv API is free and reliable.
arXiv covers most ML optimization papers which is appropriate for this hypothesis.
"""
import os
import json
import hashlib
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from config import CONFIG


ARXIV_API_URL = "https://export.arxiv.org/api/query"

# arXiv rate limit: 1 request per 3 seconds (recommended)
RATE_LIMIT_DELAY = 3.5


def build_query(dataset_name: str) -> str:
    """Build optimization-focused search query for dataset.

    Extracts canonical dataset name and queries for optimization papers.
    """
    import re

    name = dataset_name.lower()

    # Extract canonical dataset name before any parameters (seed_, nrows_, etc.)
    # Pattern: take everything before common parameter markers
    param_markers = ["seed_", "nrows_", "ncols_", "nclasses_", "stratify_"]
    for marker in param_markers:
        if marker in name:
            name = name.split(marker)[0].rstrip("_")
            break

    # Clean common suffixes
    name = name.replace("_", "-")
    for suffix in ["784", "small", "balanced", "-rotation"]:
        name = name.replace(suffix, "").strip("-")

    # Remove any remaining numbers/noise
    name = re.sub(r'\d+', '', name).strip("-").strip()
    name = re.sub(r'-+', '-', name)  # Collapse multiple dashes

    # Quote the dataset name for exact match, add optimization terms
    if not name:
        name = dataset_name.split("_")[0].lower()  # Fallback to first word

    return f'all:"{name}" AND (all:architecture OR all:NAS OR all:hyperparameter OR all:optimization)'


def _cache_path(query: str) -> str:
    key = hashlib.md5(query.encode()).hexdigest()
    return os.path.join(CONFIG.cache_dir, f"arxiv_{key}.json")


def _query_arxiv(query: str) -> int:
    """Query arXiv API and return total paper count.

    Uses totalResults from opensearch metadata - no need to paginate.
    """
    params = urllib.parse.urlencode({
        "search_query": query,
        "max_results": 1,  # Only need total count, not results
    })
    url = f"{ARXIV_API_URL}?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BibliometricStudy/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            xml_data = response.read().decode("utf-8")

        # Parse XML to get totalResults
        root = ET.fromstring(xml_data)
        # Find opensearch:totalResults element
        for elem in root.iter():
            if elem.tag.endswith("totalResults"):
                return int(elem.text)

        return 0

    except Exception as e:
        print(f"arXiv API error: {e}")
        return 0


def count_optimization_papers(dataset_name: str, use_cache: bool = True) -> int:
    """Count papers about architecture/hyperparameter optimization for dataset.

    Uses arXiv API with caching.
    """
    query = build_query(dataset_name)
    path = _cache_path(query)

    # Check cache first
    if use_cache and os.path.exists(path):
        with open(path) as f:
            cached = json.load(f)
            # Only use cache if from arXiv API (not old mock data)
            if cached.get("source") == "arxiv_api":
                return cached["count"]

    # Rate limit delay
    time.sleep(RATE_LIMIT_DELAY)

    # Query arXiv
    count = _query_arxiv(query)

    # Cache result
    if use_cache:
        os.makedirs(os.path.dirname(path), exist_ok=True) if not os.path.exists(os.path.dirname(path)) else None
        with open(path, "w") as f:
            json.dump({
                "query": query,
                "count": count,
                "source": "arxiv_api",
                "dataset_name": dataset_name
            }, f)

    return count
