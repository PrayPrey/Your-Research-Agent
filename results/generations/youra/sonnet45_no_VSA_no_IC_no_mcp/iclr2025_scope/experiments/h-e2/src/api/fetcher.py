import time
from typing import Dict

class MetadataFetcher:
    """Query Papers with Code and HuggingFace APIs."""

    def __init__(self, retry_count: int = 3, rate_limit: float = 0.1, timeout: int = 10):
        self.retry_count = retry_count
        self.rate_limit = rate_limit
        self.timeout = timeout

        # Initialize HuggingFace datasets
        try:
            from datasets import list_datasets
            self.hf_datasets = set(d.lower() for d in list_datasets())
        except Exception as e:
            print(f"WARNING: HuggingFace datasets unavailable: {e}")
            self.hf_datasets = set()

        # Initialize Papers with Code client
        try:
            from paperswithcode import PapersWithCodeClient
            self.client = PapersWithCodeClient(timeout=timeout)
        except Exception as e:
            print(f"WARNING: Papers with Code client unavailable: {e}")
            self.client = None

    def check_pwc(self, dataset_name: str) -> bool:
        """Check if dataset in Papers with Code."""
        if self.client is None:
            return False

        for attempt in range(self.retry_count):
            try:
                time.sleep(self.rate_limit)
                results = self.client.paper_list(dataset=dataset_name).results
                return len(results) > 0
            except Exception as e:
                if attempt == self.retry_count - 1:
                    return False
                time.sleep(2 ** attempt)
        return False

    def check_hf(self, dataset_name: str) -> bool:
        """Check if dataset in HuggingFace."""
        return dataset_name.lower() in self.hf_datasets

    def check_coverage(self, dataset_name: str) -> Dict[str, bool]:
        """Check both APIs."""
        pwc = self.check_pwc(dataset_name)
        hf = self.check_hf(dataset_name)
        return {"pwc": pwc, "hf": hf, "covered": pwc or hf}
