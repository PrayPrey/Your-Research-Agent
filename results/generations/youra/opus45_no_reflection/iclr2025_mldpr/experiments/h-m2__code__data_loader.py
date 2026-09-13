"""Data loading for PWC datasets and Semantic Scholar fallback."""
import time
import requests
from datasets import load_dataset
from config import SemanticScholarConfig, PWC_DATASET_ID, PWC_SPLIT


class RateLimiter:
    def __init__(self, max_per_min: int = 100):
        self.max_per_min = max_per_min
        self.interval = 60.0 / max_per_min
        self.last_call = 0.0

    def wait(self) -> None:
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        self.last_call = time.time()


def load_pwc_datasets(dataset_id: str = PWC_DATASET_ID) -> list[dict]:
    """Load PWC datasets via HF datasets lib."""
    print(f"Loading {dataset_id}...")
    ds = load_dataset(dataset_id, split=PWC_SPLIT)
    records = [dict(row) for row in ds]
    print(f"Loaded {len(records)} datasets from PWC")
    return records


def fetch_semantic_scholar_date(paper_title: str, session: requests.Session = None,
                                config: SemanticScholarConfig = None) -> str | None:
    """Query Semantic Scholar for paper publication date by title."""
    if config is None:
        config = SemanticScholarConfig()
    if session is None:
        session = requests.Session()

    url = f"{config.base_url}/paper/search"
    params = {"query": paper_title, "fields": "publicationDate", "limit": 1}

    for attempt in range(config.max_retries):
        try:
            resp = session.get(url, params=params, timeout=config.timeout_sec)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("data"):
                    return data["data"][0].get("publicationDate")
            elif resp.status_code == 429:
                time.sleep(config.retry_backoff_sec * (attempt + 1))
                continue
            return None
        except (requests.RequestException, KeyError):
            time.sleep(config.retry_backoff_sec)
    return None
