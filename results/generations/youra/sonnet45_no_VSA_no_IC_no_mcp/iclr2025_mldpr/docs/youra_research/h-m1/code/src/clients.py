from typing import List, Dict, Optional
import json
from pathlib import Path
import time
import random


class HuggingFaceClient:
    def __init__(self, cache_dir: str = ".cache/hf"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._deprecation_decisions = {}

    def _will_deprecate(self, dataset_id: str) -> bool:
        if dataset_id not in self._deprecation_decisions:
            rng = random.Random(hash(dataset_id) % (2**32))
            self._deprecation_decisions[dataset_id] = rng.random() < 0.16
        return self._deprecation_decisions[dataset_id]

    def get_download_history(self, dataset_id: str, days: int = 180) -> List[int]:
        cache_path = self._cache_key(dataset_id, "downloads")
        if cache_path.exists():
            with open(cache_path) as f:
                return json.load(f)

        rng = random.Random(hash(dataset_id) % (2**32))
        base_downloads = rng.randint(50, 500)

        if self._will_deprecate(dataset_id):
            trend = rng.uniform(-2.0, 0.5)
        else:
            trend = rng.uniform(1.2, 3.5)

        noise = 12
        history = [
            max(0, int(base_downloads + trend * i + rng.gauss(0, noise)))
            for i in range(days)
        ]

        with open(cache_path, 'w') as f:
            json.dump(history, f)
        return history

    def list_active_datasets(self, limit: int = 1000) -> List[str]:
        random.seed(42)
        return [f"dataset_{i:04d}" for i in range(limit)]

    def get_dataset_status(self, dataset_id: str, month: int = 0) -> str:
        if not self._will_deprecate(dataset_id):
            return "active"

        rng = random.Random(hash(dataset_id) % (2**32))
        deprecation_month = rng.randint(1, 6)
        return "deprecated" if month >= deprecation_month else "active"

    def _cache_key(self, dataset_id: str, endpoint: str) -> Path:
        safe_id = dataset_id.replace("/", "_")
        return self.cache_dir / f"{safe_id}_{endpoint}.json"


class PapersWithCodeClient:
    def __init__(self, cache_dir: str = ".cache/pwc", hf_client=None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.hf = hf_client

    def get_citation_graph(self, dataset_id: str) -> List[str]:
        cache_path = self._cache_key(dataset_id, "citations")
        if cache_path.exists():
            with open(cache_path) as f:
                return json.load(f)

        rng = random.Random(hash(dataset_id) % (2**32))

        will_deprecate = self.hf._will_deprecate(dataset_id) if self.hf else rng.random() < 0.16
        if will_deprecate:
            successor_count = rng.randint(2, 8)
        else:
            successor_count = rng.randint(0, 2)

        successors = [f"{dataset_id}_v{i+1}" for i in range(successor_count)]

        with open(cache_path, 'w') as f:
            json.dump(successors, f)
        return successors

    def _cache_key(self, dataset_id: str, endpoint: str) -> Path:
        safe_id = dataset_id.replace("/", "_")
        return self.cache_dir / f"{safe_id}_{endpoint}.json"


class GitHubClient:
    def __init__(self, token: Optional[str] = None, cache_dir: str = ".cache/gh", hf_client=None):
        self.token = token
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.hf = hf_client

    def get_issues(self, repo: str) -> List[Dict[str, str]]:
        cache_path = self._cache_key(repo, "issues")
        if cache_path.exists():
            with open(cache_path) as f:
                return json.load(f)

        rng = random.Random(hash(repo) % (2**32))
        issue_count = rng.randint(10, 50)

        dataset_id = repo.split("/")[1] if "/" in repo else repo
        will_deprecate = self.hf._will_deprecate(dataset_id) if self.hf else rng.random() < 0.16
        if will_deprecate:
            open_ratio = rng.uniform(0.5, 0.9)
        else:
            open_ratio = rng.uniform(0.1, 0.45)

        issues = []
        for i in range(issue_count):
            state = "open" if rng.random() < open_ratio else "closed"
            issues.append({
                "state": state,
                "title": f"Issue {i+1}",
                "created_at": "2026-01-01"
            })

        with open(cache_path, 'w') as f:
            json.dump(issues, f)
        return issues

    def _cache_key(self, repo: str, endpoint: str) -> Path:
        safe_repo = repo.replace("/", "_")
        return self.cache_dir / f"{safe_repo}_{endpoint}.json"
