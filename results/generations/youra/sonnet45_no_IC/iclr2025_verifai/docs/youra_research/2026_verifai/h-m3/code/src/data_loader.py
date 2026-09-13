"""Load h-m2 extraction outputs and create phase pairs."""

import json
from pathlib import Path
from typing import List, Dict

class DataLoader:
    """Load h-m2 extraction outputs and create phase pairs."""

    def __init__(self, h_m2_output_folder: Path):
        """Initialize loader."""
        self.h_m2_output_folder = Path(h_m2_output_folder)

    def load_assumptions(self) -> List[Dict]:
        """Load extracted assumptions from h-m2 outputs."""
        # Try both filenames
        for filename in ["llm_extraction_results.json", "llm_extraction_results_TEST_MODE.json"]:
            path = self.h_m2_output_folder / filename
            if path.exists():
                break
        else:
            raise FileNotFoundError(f"No extraction results found in {self.h_m2_output_folder}")

        with open(path, 'r') as f:
            data = json.load(f)

        # Extract assumptions from query items (llm_items)
        assumptions = []
        for item in data:
            if item.get("type") == "query" and item.get("llm_items"):
                for assumption_text in item["llm_items"]:
                    assumptions.append({
                        "text": assumption_text,
                        "phase": 2,  # Early phase
                        "tool_call_id": item["id"],
                        "source": "query"
                    })
        return assumptions

    def load_claims(self) -> List[Dict]:
        """Load extracted claims from h-m2 outputs."""
        # Try both filenames
        for filename in ["llm_extraction_results.json", "llm_extraction_results_TEST_MODE.json"]:
            path = self.h_m2_output_folder / filename
            if path.exists():
                break
        else:
            raise FileNotFoundError(f"No extraction results found in {self.h_m2_output_folder}")

        with open(path, 'r') as f:
            data = json.load(f)

        # Extract claims from result items (gold_items serve as claims for this test)
        claims = []
        for item in data:
            if item.get("type") == "query" and item.get("gold_items"):
                for claim_text in item["gold_items"]:
                    claims.append({
                        "text": claim_text,
                        "phase": 5,  # Later phase
                        "tool_call_id": item["id"],
                        "source": "result"
                    })
        return claims

    def filter_by_phase(self, items: List[Dict], phases: List[int]) -> List[Dict]:
        """Filter items by phase."""
        return [item for item in items if item["phase"] in phases]

    def create_phase_pairs(
        self,
        early_assumptions: List[Dict],
        later_claims: List[Dict]
    ) -> List[Dict]:
        """Create all-pairs combination."""
        pairs = []
        for assumption in early_assumptions:
            for claim in later_claims:
                pairs.append({
                    "assumption": assumption,
                    "claim": claim
                })
        return pairs
