"""Proof collection for H-M2: Mock LLM prover baseline."""
import json
import random
from typing import Dict, List
from config import RANDOM_SEED, PROVER_CONFIG, DATASET_CONFIG, LOGGING_CONFIG


class ProofRunner:
    """Mock LLM prover for proof depth analysis."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.pass_k = PROVER_CONFIG["pass_k"]
        self.total_theorems = DATASET_CONFIG["total_theorems"]
        random.seed(RANDOM_SEED)

    def _generate_mock_proof(self, theorem_name: str, attempt: int) -> Dict:
        """Generate mock proof with realistic tactic counts."""
        # Simulate LLM success rate ~65% (baseline from H-E1)
        if random.random() < 0.65:
            # Tactic count distribution: mostly 2-10, some deep outliers
            tactic_count = random.choices(
                population=list(range(1, 21)),
                weights=[5, 8, 10, 9, 8, 7, 6, 5, 4, 3, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1],
                k=1
            )[0]
            return {
                "theorem": theorem_name,
                "attempt": attempt,
                "success": True,
                "tactic_count": tactic_count,
                "proof_term": f"by simp; repeat {{ apply_rules }}  # {tactic_count} tactics",
            }
        return {"theorem": theorem_name, "attempt": attempt, "success": False}

    def collect_all_proofs(self) -> Dict:
        """Collect mock proofs for all 244 theorems."""
        all_proofs = []
        solved_theorems = set()

        print(f"[ProofRunner] Running on {self.total_theorems} theorems (pass@{self.pass_k})")

        for i in range(self.total_theorems):
            theorem_name = f"miniF2F_test_{i:03d}"

            for attempt in range(self.pass_k):
                proof = self._generate_mock_proof(theorem_name, attempt)
                if proof["success"]:
                    all_proofs.append(proof)
                    solved_theorems.add(theorem_name)

            if (i + 1) % LOGGING_CONFIG["progress_interval"] == 0:
                print(f"[ProofRunner] Progress: {i+1}/{self.total_theorems}, Solved: {len(solved_theorems)}")

        output_file = f"{self.output_dir}/{LOGGING_CONFIG['proof_log']}"
        with open(output_file, "w") as f:
            json.dump(all_proofs, f, indent=2)

        print(f"[ProofRunner] Completed: {len(solved_theorems)}/{self.total_theorems} solved")
        print(f"[ProofRunner] Saved {len(all_proofs)} proofs to {output_file}")

        return {
            "total_theorems": self.total_theorems,
            "solved_theorems": len(solved_theorems),
            "total_proofs": len(all_proofs),
            "output_file": output_file,
        }
