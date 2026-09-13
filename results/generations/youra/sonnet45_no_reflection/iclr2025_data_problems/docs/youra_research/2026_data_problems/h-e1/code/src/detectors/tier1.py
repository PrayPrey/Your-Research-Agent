"""Tier 1: Data-Layer Filters - Temporal isolation + LSH fingerprinting"""
from datasketch import MinHash, MinHashLSH
from datetime import datetime
from typing import List, Dict, Optional

class Tier1DataFilter:
    """
    Tier 1 Detection: Data-layer filters
    - Temporal isolation (timestamp check)
    - LSH-based structural fingerprinting (near-duplicate detection)
    """

    def __init__(
        self,
        temporal_cutoff: str = "2021-11-01",
        lsh_num_perm: int = 128,
        lsh_bands: int = 20,
        lsh_rows: int = 5
    ):
        self.release_date = datetime.fromisoformat(temporal_cutoff)
        self.lsh = MinHashLSH(
            threshold=0.5,  # Jaccard similarity threshold
            num_perm=lsh_num_perm,
            params=(lsh_bands, lsh_rows)
        )
        self.indexed_samples = {}

    def check_temporal_isolation(
        self,
        sample_timestamp: Optional[str]
    ) -> bool:
        """
        Check if sample timestamp is after benchmark release date
        Returns True if contamination detected
        """
        if sample_timestamp is None:
            return False

        try:
            sample_date = datetime.fromisoformat(sample_timestamp)
            return sample_date >= self.release_date
        except:
            return False

    def check_lsh_fingerprint(self, sample_text: str, sample_id: str = None) -> bool:
        """
        Check if sample is near-duplicate using LSH
        Returns True if contamination detected (near-duplicate found)
        """
        # Create MinHash for sample
        minhash = MinHash(num_perm=128)
        for word in sample_text.lower().split():
            minhash.update(word.encode('utf-8'))

        # Query LSH index
        matches = self.lsh.query(minhash)

        if len(matches) > 0:
            # Near-duplicate found
            return True

        # Add to index if provided sample_id
        if sample_id:
            self.lsh.insert(sample_id, minhash)
            self.indexed_samples[sample_id] = sample_text

        return False

    def detect(
        self,
        sample: Dict,
        sample_id: str = None,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Combined detection using OR logic
        Returns True if contamination detected by either filter
        """
        # Extract sample text
        sample_text = sample.get('question', '') + ' ' + sample.get('answer', '')

        # Check temporal isolation
        temporal_detected = self.check_temporal_isolation(timestamp)

        # Check LSH fingerprint
        lsh_detected = self.check_lsh_fingerprint(sample_text, sample_id)

        # OR logic
        return temporal_detected or lsh_detected

    def index_benchmark(self, benchmark_samples: List[Dict]):
        """Index benchmark samples for LSH matching"""
        for idx, sample in enumerate(benchmark_samples):
            sample_text = sample.get('question', '') + ' ' + sample.get('answer', '')
            sample_id = f"benchmark_{idx}"

            # Create MinHash
            minhash = MinHash(num_perm=128)
            for word in sample_text.lower().split():
                minhash.update(word.encode('utf-8'))

            # Insert into LSH
            self.lsh.insert(sample_id, minhash)
            self.indexed_samples[sample_id] = sample_text
