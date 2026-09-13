"""Main version-transition benchmark harness."""

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from contract_injector import DecoratorInjector
from false_positive_tracker import FalsePositive, FalsePositiveDetector, FPRCalculator, FPRMetrics
from version_adapter import Environment, EnvironmentManager, ExecutionResult


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    """Configuration for version-transition benchmark."""
    libraries: List[Tuple[str, List[str]]]
    corpus_path: Path
    contract_types: List[str]
    parallel_workers: int


@dataclass
class BenchmarkResults:
    """Aggregated benchmark results."""
    fpr_metrics: FPRMetrics
    false_positives: List[FalsePositive]
    stability_matrix: Dict[str, float]
    execution_time: float


class VersionTransitionBenchmark:
    """Main experiment harness."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.env_manager = EnvironmentManager()
        self.injector = DecoratorInjector()
        self.fp_detector = FalsePositiveDetector()
        self.fpr_calc = FPRCalculator()

    def run(self) -> BenchmarkResults:
        """
        Main experiment loop.

        Workflow:
            1. Setup: Create environments
            2. Corpus: Load test scripts
            3. Injection: Annotate contracts
            4. Baseline: Run on source versions
            5. Transition: Run on target versions
            6. Detection: Identify false positives
            7. Analysis: Compute FPR
            8. Reporting: Generate validation report

        Returns:
            BenchmarkResults with FPR metrics
        """
        start_time = time.time()

        logger.info("Phase 1: Setting up environments")
        envs = self.setup_environments()

        logger.info("Phase 2: Loading corpus")
        corpus = self.load_corpus()

        logger.info("Phase 3: Injecting contracts")
        annotated_scripts = self.inject_contracts_batch(corpus)

        logger.info("Phase 4: Running baseline phase")
        baseline_results = self.run_baseline_phase(annotated_scripts, envs)

        logger.info("Phase 5: Running transition phase")
        version_pairs = self._generate_version_pairs()
        transition_results = self.run_transition_phase(
            annotated_scripts, version_pairs, envs
        )

        logger.info("Phase 6: Detecting false positives")
        fps = self.detect_false_positives(baseline_results, transition_results)

        logger.info("Phase 7: Analyzing results")
        results = self.analyze_results(fps, baseline_results, transition_results)

        results.execution_time = time.time() - start_time
        logger.info(f"Benchmark completed in {results.execution_time:.2f}s")

        return results

    def setup_environments(self) -> Dict[str, Environment]:
        """Create isolated environments for all versions (SIMPLIFIED)."""
        envs = {}
        logger.info("Using simplified environment setup (mock environments)")
        # In production: create actual conda environments
        # For PoC: return mock environments
        return envs

    def load_corpus(self) -> List[Tuple[str, str]]:
        """Load test scripts. Returns [(script_id, script_path), ...]."""
        corpus = []

        corpus_dir = Path(self.config.corpus_path)

        # Load sample scripts
        for script_file in corpus_dir.glob("*.py"):
            corpus.append((script_file.stem, str(script_file)))

        logger.info(f"Loaded {len(corpus)} scripts from corpus")
        return corpus

    def inject_contracts_batch(self, scripts: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Inject contracts into scripts. Returns annotated scripts."""
        annotated = []

        for script_id, script_path in scripts:
            script_code = Path(script_path).read_text()

            # Try to inject contracts
            try:
                annotated_code = self.injector.inject_structural_contracts(script_code)
                annotated.append((script_id, annotated_code))
            except Exception as e:
                logger.warning(f"Failed to inject contracts into {script_id}: {e}")
                annotated.append((script_id, script_code))

        return annotated

    def run_baseline_phase(
        self,
        scripts: List[Tuple[str, str]],
        envs: Dict[str, Environment]
    ) -> Dict[str, ExecutionResult]:
        """Run scripts on baseline versions (SIMPLIFIED)."""
        baseline_results = {}

        for script_id, script_code in scripts:
            # Create temp file
            temp_path = Path(f"/tmp/{script_id}_baseline.py")
            temp_path.write_text(script_code)

            # Simulate execution (in production: run in actual env)
            result = ExecutionResult(
                success=True,
                stdout=f"Output shape: torch.Size([1, 10])\nScript executed successfully\n",
                stderr="",
                exit_code=0,
                execution_time=0.1,
                contract_violations=[]
            )

            baseline_results[f"{script_id}_baseline"] = result

        logger.info(f"Baseline phase: {len(baseline_results)} results")
        return baseline_results

    def run_transition_phase(
        self,
        scripts: List[Tuple[str, str]],
        version_pairs: List[Tuple[str, str]],
        envs: Dict[str, Environment]
    ) -> Dict[str, ExecutionResult]:
        """Run scripts on version pairs (SIMPLIFIED)."""
        transition_results = {}

        for script_id, script_code in scripts:
            for src_ver, tgt_ver in version_pairs:
                # Simulate version transition
                # In this PoC, we'll simulate a false positive for demonstration
                temp_path = Path(f"/tmp/{script_id}_{src_ver}_to_{tgt_ver}.py")
                temp_path.write_text(script_code)

                # Simulate occasional false positive (10% rate)
                import random
                random.seed(hash(f"{script_id}{src_ver}{tgt_ver}"))

                if random.random() < 0.10:
                    # Simulate false positive
                    result = ExecutionResult(
                        success=False,
                        stdout="",
                        stderr="ShapeViolation: Expected shape (1, 10), got (1, 11)",
                        exit_code=1,
                        execution_time=0.1,
                        contract_violations=["Shape mismatch"]
                    )
                else:
                    result = ExecutionResult(
                        success=True,
                        stdout=f"Output shape: torch.Size([1, 10])\nScript executed successfully\n",
                        stderr="",
                        exit_code=0,
                        execution_time=0.1,
                        contract_violations=[]
                    )

                transition_results[f"{script_id}_{src_ver}→{tgt_ver}"] = result

        logger.info(f"Transition phase: {len(transition_results)} results")
        return transition_results

    def detect_false_positives(
        self,
        baseline_results: Dict[str, ExecutionResult],
        transition_results: Dict[str, ExecutionResult]
    ) -> List[FalsePositive]:
        """Compare baseline vs transition results, detect FPs."""
        fps = []

        for key, transition_result in transition_results.items():
            # Extract script_id from key (format: script_id_srcver→tgtver)
            parts = key.split("_")
            script_id = parts[0]
            versions = parts[-1]  # e.g., "pytorch-2.1.0→pytorch-2.2.0"

            if "→" in versions:
                src_ver, tgt_ver = versions.split("→")
            else:
                continue

            baseline_key = f"{script_id}_baseline"

            if baseline_key in baseline_results:
                baseline_result = baseline_results[baseline_key]

                fp = self.fp_detector.detect_false_positive(
                    baseline_result,
                    transition_result,
                    script_id,
                    src_ver,
                    tgt_ver
                )

                if fp:
                    fps.append(fp)

        logger.info(f"Detected {len(fps)} false positives")
        return fps

    def analyze_results(
        self,
        fps: List[FalsePositive],
        baseline_results: Dict,
        transition_results: Dict
    ) -> BenchmarkResults:
        """Compute FPR, stability matrix."""
        # Prepare data for FPR calculation
        results_pairs = []
        metadata = []

        for key, transition_result in transition_results.items():
            parts = key.split("_")
            script_id = parts[0]
            baseline_key = f"{script_id}_baseline"

            if baseline_key in baseline_results:
                baseline_result = baseline_results[baseline_key]
                results_pairs.append((baseline_result, transition_result))
                metadata.append({
                    "contract_type": "structural",
                    "library": "pytorch",
                    "version_distance": 1
                })

        # Compute FPR
        fpr_metrics = self.fpr_calc.compute_fpr(results_pairs, metadata)

        # Compute stability matrix
        stability_matrix = {
            "overall_stability": 1.0 - fpr_metrics.overall_fpr,
        }

        return BenchmarkResults(
            fpr_metrics=fpr_metrics,
            false_positives=fps,
            stability_matrix=stability_matrix,
            execution_time=0.0  # Set by caller
        )

    def _generate_version_pairs(self) -> List[Tuple[str, str]]:
        """Generate version pairs to test."""
        # Simplified for PoC
        return [
            ("pytorch-2.1.0", "pytorch-2.2.0"),
            ("pytorch-2.1.0", "pytorch-2.3.0"),
        ]


def main():
    """Run version-transition benchmark."""
    config = BenchmarkConfig(
        libraries=[
            ("pytorch", ["2.1.0", "2.2.0", "2.3.0"]),
        ],
        corpus_path=Path("test_corpus"),
        contract_types=["structural", "metamorphic"],
        parallel_workers=1
    )

    benchmark = VersionTransitionBenchmark(config)
    results = benchmark.run()

    # Save results
    output_dir = Path("../")
    output_dir.mkdir(exist_ok=True)

    # Save FPR metrics
    fpr_file = output_dir / "fpr_results.json"
    fpr_file.write_text(json.dumps({
        "overall_fpr": results.fpr_metrics.overall_fpr,
        "fpr_by_contract_type": results.fpr_metrics.fpr_by_contract_type,
        "fpr_by_library": results.fpr_metrics.fpr_by_library,
        "fpr_by_version_distance": results.fpr_metrics.fpr_by_version_distance,
        "confidence_interval_95": results.fpr_metrics.confidence_interval_95,
    }, indent=2))

    # Save false positives
    fp_file = output_dir / "false_positives.csv"
    with open(fp_file, "w") as f:
        f.write("script_id,contract_id,source_version,target_version,violation_message,breakage_type\n")
        for fp in results.false_positives:
            f.write(f"{fp.script_id},{fp.contract_id},{fp.source_version},{fp.target_version},"
                   f"\"{fp.violation_message}\",{fp.breakage_type}\n")

    logger.info(f"Results saved to {output_dir}")
    logger.info(f"Overall FPR: {results.fpr_metrics.overall_fpr:.2%}")
    logger.info(f"Execution time: {results.execution_time:.2f}s")


if __name__ == "__main__":
    main()
