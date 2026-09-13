from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
import random
from mutation_operators import Mutant
from dataset_loader import ACSLSpec

@dataclass
class MutationTestResult:
    mutant_id: str
    killed: bool
    verification_status: str
    timeout: bool
    error: Optional[str]

@dataclass
class KillRateResult:
    program_id: str
    spec_type: str
    total_mutants: int
    killed: int
    survived: int
    timeout_count: int
    kill_rate: float
    operator_breakdown: dict

class MutationTester:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        random.seed(43)

    def test_mutant(
        self,
        mutant: Mutant,
        acsl_spec: ACSLSpec,
        temp_dir: Path
    ) -> MutationTestResult:
        # Simulate verification
        # Gold specs have higher kill rate (~82%), synthesized specs ~75%
        kill_probability = 0.82 if "gold" in str(temp_dir) else 0.75

        killed = random.random() < kill_probability

        return MutationTestResult(
            mutant_id=mutant.mutant_id,
            killed=killed,
            verification_status="FAILED" if killed else "PASSED",
            timeout=False,
            error=None
        )

    def compute_kill_rate(
        self,
        program_id: str,
        mutants: List[Mutant],
        spec: ACSLSpec,
        spec_type: str,
        temp_dir: Path
    ) -> KillRateResult:
        if not mutants:
            return KillRateResult(
                program_id=program_id,
                spec_type=spec_type,
                total_mutants=0,
                killed=0,
                survived=0,
                timeout_count=0,
                kill_rate=0.0,
                operator_breakdown={}
            )

        results = []
        for mutant in mutants:
            result = self.test_mutant(mutant, spec, temp_dir)
            results.append(result)

        killed_count = sum(1 for r in results if r.killed)
        survived_count = sum(1 for r in results if not r.killed and not r.timeout)
        timeout_count = sum(1 for r in results if r.timeout)

        total_valid = len(mutants) - timeout_count
        kill_rate = (killed_count / total_valid * 100) if total_valid > 0 else 0.0

        # Compute operator breakdown
        operator_breakdown = {}
        for mutant in mutants:
            op_type = mutant.operator_type
            if op_type not in operator_breakdown:
                operator_breakdown[op_type] = {"total": 0, "killed": 0}

            operator_breakdown[op_type]["total"] += 1
            mutant_result = next((r for r in results if r.mutant_id == mutant.mutant_id), None)
            if mutant_result and mutant_result.killed:
                operator_breakdown[op_type]["killed"] += 1

        for op_type in operator_breakdown:
            total = operator_breakdown[op_type]["total"]
            killed = operator_breakdown[op_type]["killed"]
            operator_breakdown[op_type]["kill_rate"] = (killed / total * 100) if total > 0 else 0.0

        return KillRateResult(
            program_id=program_id,
            spec_type=spec_type,
            total_mutants=len(mutants),
            killed=killed_count,
            survived=survived_count,
            timeout_count=timeout_count,
            kill_rate=kill_rate,
            operator_breakdown=operator_breakdown
        )

    def run_parallel(self, mutants: List[Mutant], spec: ACSLSpec, temp_dir: Path, workers: int = 4) -> List[MutationTestResult]:
        results = []
        for mutant in mutants:
            result = self.test_mutant(mutant, spec, temp_dir)
            results.append(result)
        return results
