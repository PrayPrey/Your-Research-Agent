from typing import List, Dict, Any
from pathlib import Path
from src.clients import HuggingFaceClient, PapersWithCodeClient, GitHubClient
import json


class DataCollector:
    def __init__(
        self,
        hf_client: HuggingFaceClient,
        pwc_client: PapersWithCodeClient,
        gh_client: GitHubClient,
        output_dir: Path
    ):
        self.hf = hf_client
        self.pwc = pwc_client
        self.gh = gh_client
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def collect_dataset_data(self, dataset_id: str, repo: str) -> Dict[str, Any]:
        download_history = self.hf.get_download_history(dataset_id)
        successors = self.pwc.get_citation_graph(dataset_id)
        issues = self.gh.get_issues(repo)

        return {
            'dataset_id': dataset_id,
            'download_history': download_history,
            'successors': successors,
            'issues': issues,
            'repo': repo
        }

    def collect_batch(
        self,
        dataset_ids: List[str],
        repos: List[str]
    ) -> List[Dict[str, Any]]:
        results = []
        total = len(dataset_ids)
        for i, (dataset_id, repo) in enumerate(zip(dataset_ids, repos)):
            if (i + 1) % 100 == 0:
                print(f"Collecting {i+1}/{total}: {dataset_id}")
            data = self.collect_dataset_data(dataset_id, repo)
            results.append(data)
        return results

    def save_collected_data(self, data: List[Dict], path: str) -> None:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
