"""Tactic extraction for H-M2: Extract tactic counts from proofs."""
import json
import csv
from typing import List, Dict
from config import LOGGING_CONFIG


class TacticExtractor:
    """Extract tactic counts from proof data."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def process_proofs(self) -> Dict:
        """Process proofs and extract tactic counts."""
        proof_file = f"{self.output_dir}/{LOGGING_CONFIG['proof_log']}"
        output_csv = f"{self.output_dir}/{LOGGING_CONFIG['tactic_counts']}"

        with open(proof_file, "r") as f:
            proofs = json.load(f)

        # Group proofs by theorem
        theorem_depths = {}
        for proof in proofs:
            if proof["success"]:
                theorem = proof["theorem"]
                tactic_count = proof["tactic_count"]
                if theorem not in theorem_depths:
                    theorem_depths[theorem] = []
                theorem_depths[theorem].append(tactic_count)

        # Find minimum depth per theorem
        tactic_data = []
        for theorem, depths in theorem_depths.items():
            min_depth = min(depths)
            max_depth = max(depths)
            tactic_data.append({
                "theorem": theorem,
                "min_tactic_count": min_depth,
                "max_tactic_count": max_depth,
                "num_proofs": len(depths),
            })

        # Write CSV
        with open(output_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["theorem", "min_tactic_count", "max_tactic_count", "num_proofs"])
            writer.writeheader()
            writer.writerows(tactic_data)

        print(f"[TacticExtractor] Processed {len(tactic_data)} theorems")
        print(f"[TacticExtractor] Saved tactic counts to {output_csv}")

        return {
            "processed_theorems": len(tactic_data),
            "output_file": output_csv,
        }
