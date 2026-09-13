"""Data loader for H-E1 retrospective corpus."""

import json
from pathlib import Path
from typing import Dict, List, Tuple


class CorpusLoader:
    """Load and parse H-E1 retrospective corpus."""

    def __init__(self, corpus_path: str):
        """Initialize with corpus file path."""
        self.corpus_path = Path(corpus_path)

    def load(self) -> List[Dict]:
        """Load corpus from JSON file. Returns list of paper dicts."""
        with open(self.corpus_path, 'r') as f:
            corpus = json.load(f)

        if not isinstance(corpus, list):
            raise ValueError(f"Expected list, got {type(corpus)}")

        print(f"Loaded {len(corpus)} papers from {self.corpus_path}")
        return corpus

    def extract_overhead_arrays(self, corpus: List[Dict]) -> Tuple[List[float], List[float]]:
        """
        Extract (O_10, O_full) overhead arrays.
        Returns: (micro_pilot_overhead, full_scale_overhead)
        """
        o10 = []
        ofull = []

        for paper in corpus:
            measurements = paper["overhead_measurements"]
            o10.append(measurements["micro_pilot"]["overhead_percent"])
            ofull.append(measurements["full_scale"]["overhead_percent"])

        return o10, ofull

    def group_by_type(self, corpus: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group papers by hypothesis_type.
        Returns: {type: [papers]}
        """
        grouped = {}
        for paper in corpus:
            hyp_type = paper["hypothesis_type"]
            if hyp_type not in grouped:
                grouped[hyp_type] = []
            grouped[hyp_type].append(paper)

        print(f"Grouped into {len(grouped)} types: {list(grouped.keys())}")
        for hyp_type, papers in grouped.items():
            print(f"  {hyp_type}: {len(papers)} papers")

        return grouped
