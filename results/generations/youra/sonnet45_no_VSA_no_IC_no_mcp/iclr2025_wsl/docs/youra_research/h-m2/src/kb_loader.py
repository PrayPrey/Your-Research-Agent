"""Load knowledge base from h-m1."""
import yaml
from pathlib import Path
from typing import List, Dict

class KBLoader:
    def __init__(self, kb_path: str):
        self.kb_path = Path(kb_path)
        self.triples: List[Dict[str, str]] = []

    def load(self) -> List[Dict[str, str]]:
        """Load KB YAML from h-m1. Returns list of {dataset, benchmark, metric} dicts."""
        if not self.kb_path.exists():
            raise FileNotFoundError(f"KB not found: {self.kb_path}")

        with open(self.kb_path) as f:
            data = yaml.safe_load(f)

        self.triples = data.get("triples", [])
        return self.triples

    def get_datasets(self) -> List[str]:
        """Extract all dataset names."""
        return [t["dataset"] for t in self.triples]

    def get_benchmarks(self) -> List[str]:
        """Extract all benchmark names."""
        return [t["benchmark"] for t in self.triples]

    def get_metrics(self) -> List[str]:
        """Extract all metric names."""
        return [t["metric"] for t in self.triples]


if __name__ == "__main__":
    # Self-check
    kb = KBLoader("../../h-m1/data/pwc_cache/kb.yaml")
    triples = kb.load()
    assert len(triples) > 0, "KB empty"
    assert "dataset" in triples[0], "Missing dataset field"
    assert "benchmark" in triples[0], "Missing benchmark field"
    assert "metric" in triples[0], "Missing metric field"
    print(f"KB loaded: {len(triples)} triples")
