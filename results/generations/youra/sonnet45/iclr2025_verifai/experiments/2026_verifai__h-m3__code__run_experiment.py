#!/usr/bin/env python3
"""
H-M3: Conditional Execution Gating Token Efficiency
Tests whether CASCADE routing (mypy → if clean → pytest) maintains ≤15% token overhead vs AGGREGATION
"""
import json
import logging
import sys
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('experiment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ExperimentConfig:
    """H-M3 experiment configuration"""
    model_name: str = "codellama/CodeLlama-7b-hf"
    temperature: float = 0.7
    top_p: float = 0.95
    max_new_tokens: int = 512
    max_iterations: int = 10
    token_limit_per_source: int = 1000
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    efficiency_threshold: float = 1.15
    seed: int = 42
    device: str = "auto"
    h_e1_validation_path: str = "../h-e1/04_validation.md"
    output_dir: Path = Path("./outputs")
    figures_dir: Path = Path("./figures")


class HumanEvalLoader:
    """Load HumanEval+ dataset and filter to h-e1 qualified tasks"""

    def __init__(self, use_evalplus: bool = True):
        self.use_evalplus = use_evalplus
        self.problems = None

    def load_problems(self) -> Dict[str, Dict]:
        """Load all 164 tasks"""
        if self.use_evalplus:
            try:
                from evalplus.data import get_human_eval_plus
                self.problems = get_human_eval_plus()
                logger.info(f"Loaded {len(self.problems)} tasks from HumanEval+")
                return self.problems
            except ImportError:
                logger.warning("evalplus not installed, falling back to human-eval")

        from human_eval.data import read_problems
        self.problems = read_problems()
        logger.info(f"Loaded {len(self.problems)} tasks from HumanEval")
        return self.problems

    def load_qualified_task_ids(self, h_e1_validation_path: str) -> List[str]:
        """Parse N=20 dual-sensitive task IDs from h-e1 results"""
        # Try to load from h-e1 results.json first (more reliable)
        possible_json_paths = [
            Path("../h-e1/code/outputs/results.json"),
            Path("../../h-e1/code/outputs/results.json"),
            Path("../h-e1/outputs/results.json"),
        ]

        for json_path in possible_json_paths:
            if json_path.exists():
                logger.info(f"Loading qualified tasks from: {json_path}")
                with open(json_path) as f:
                    data = json.load(f)

                if "qualified_task_ids" in data:
                    task_ids = data["qualified_task_ids"][:20]  # Take first 20
                    logger.info(f"Loaded {len(task_ids)} qualified dual-sensitive tasks from h-e1 results")
                    return task_ids

        # Fallback: Try parsing from validation markdown
        possible_md_paths = [
            Path(h_e1_validation_path),
            Path("../h-e1/04_validation.md"),
            Path("../../h-e1/04_validation.md"),
        ]

        for md_path in possible_md_paths:
            if md_path.exists():
                logger.info(f"Loading qualified tasks from: {md_path}")
                with open(md_path) as f:
                    content = f.read()

                # Parse qualified task IDs from validation report
                task_ids = re.findall(r'HumanEval/\d+', content)
                task_ids = list(set(task_ids))  # Remove duplicates
                task_ids = sorted(task_ids)[:20]  # Take first 20

                if task_ids:
                    logger.info(f"Loaded {len(task_ids)} qualified dual-sensitive tasks")
                    return task_ids

        raise FileNotFoundError(f"H-E1 results not found. Tried JSON: {possible_json_paths}, MD: {possible_md_paths}")


class CodeLlamaGenerator:
    """Code generation with token counting"""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.model = None
        self.tokenizer = None

    def load_model(self) -> None:
        """Load CodeLlama-7B with FP16 and device_map='auto'"""
        logger.info(f"Loading model: {self.config.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float16,
            device_map=self.config.device
        )
        self.model.eval()
        logger.info("Model loaded successfully")

    def generate(self, prompt: str) -> str:
        """Generate code from prompt"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode only the new tokens
        generated_text = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        return generated_text

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))


class MypyVerifier:
    """Static verification with mypy --strict + feedback formatting"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def verify(self, code: str) -> Dict[str, any]:
        """Run mypy --strict on code"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            result = subprocess.run(
                ['mypy', '--strict', temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return {
                "success": result.returncode == 0,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stderr": "Mypy timed out",
                "returncode": -1
            }
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def format_feedback(self, stderr: str) -> str:
        """Format mypy errors for LLM feedback (≤1000 tokens)"""
        if not stderr:
            return "Mypy: No errors found"
        # Truncate if too long
        lines = stderr.split('\n')
        if len(lines) > 30:
            lines = lines[:30] + ["... (truncated)"]
        return "Mypy errors:\n" + '\n'.join(lines)


class PytestVerifier:
    """Execution verification with pytest + feedback formatting"""

    def __init__(self, timeout: int = 120):
        self.timeout = timeout

    def verify(self, code: str, test_code: str, entry_point: str) -> Dict[str, any]:
        """Run pytest on code with test cases"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Write solution code
            solution_file = tmpdir / "solution.py"
            solution_file.write_text(code)

            # Write test code
            test_file = tmpdir / f"test_{entry_point}.py"
            test_file.write_text(test_code)

            try:
                result = subprocess.run(
                    ['pytest', str(test_file), '-v', '--tb=short'],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tmpdir
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": "Pytest timed out",
                    "returncode": -1
                }

    def format_feedback(self, output: str) -> str:
        """Format pytest output for LLM feedback (≤1000 tokens)"""
        if not output:
            return "Tests: All passed"
        lines = output.split('\n')
        if len(lines) > 40:
            lines = lines[:40] + ["... (truncated)"]
        return "Test output:\n" + '\n'.join(lines)


class CascadeRouter:
    """Conditional feedback routing: mypy → (if clean) → pytest"""

    def __init__(self, generator: CodeLlamaGenerator, max_iterations: int = 10):
        self.generator = generator
        self.max_iterations = max_iterations
        self.mypy_verifier = MypyVerifier(timeout=10)
        self.pytest_verifier = PytestVerifier(timeout=120)

    def solve_task(self, task_prompt: str, test_code: str, entry_point: str) -> Dict:
        """Solve task with conditional gating"""
        iteration = 0
        prompt = task_prompt
        total_tokens = 0
        mypy_tokens_total = 0
        pytest_tokens_total = 0
        gating_skipped_count = 0

        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"CASCADE iteration {iteration}/{self.max_iterations}")

            # Generate code
            code = self.generator.generate(prompt)

            # Step 1: Run mypy (always)
            mypy_result = self.mypy_verifier.verify(code)
            mypy_feedback = self.mypy_verifier.format_feedback(mypy_result["stderr"])
            mypy_tokens = self.generator.count_tokens(mypy_feedback)
            total_tokens += mypy_tokens
            mypy_tokens_total += mypy_tokens

            # Step 2: Conditional gating
            if mypy_result["success"]:
                # Gate OPEN: Run pytest
                pytest_result = self.pytest_verifier.verify(code, test_code, entry_point)
                pytest_feedback = self.pytest_verifier.format_feedback(pytest_result["stdout"])
                pytest_tokens = self.generator.count_tokens(pytest_feedback)
                total_tokens += pytest_tokens
                pytest_tokens_total += pytest_tokens

                if pytest_result["success"]:
                    # Success!
                    logger.info(f"CASCADE: Task solved in {iteration} iterations")
                    return {
                        "code": code,
                        "iterations": iteration,
                        "total_tokens": total_tokens,
                        "mypy_tokens": mypy_tokens_total,
                        "pytest_tokens": pytest_tokens_total,
                        "gating_skipped_count": gating_skipped_count,
                        "success": True
                    }

                # Update prompt with pytest feedback
                prompt = prompt + f"\n\nIteration {iteration} - Tests failed:\n{pytest_feedback}\n\nPlease fix the code."
            else:
                # Gate CLOSED: Skip pytest
                gating_skipped_count += 1
                logger.info(f"CASCADE: Gate closed (mypy failed), skipping pytest")
                prompt = prompt + f"\n\nIteration {iteration} - Mypy errors:\n{mypy_feedback}\n\nPlease fix the code."

        # Max iterations reached
        logger.warning(f"CASCADE: Max iterations reached without success")
        return {
            "code": code,
            "iterations": self.max_iterations,
            "total_tokens": total_tokens,
            "mypy_tokens": mypy_tokens_total,
            "pytest_tokens": pytest_tokens_total,
            "gating_skipped_count": gating_skipped_count,
            "success": False
        }


class AggregationRouter:
    """Baseline: simultaneous mypy + pytest feedback"""

    def __init__(self, generator: CodeLlamaGenerator, max_iterations: int = 10):
        self.generator = generator
        self.max_iterations = max_iterations
        self.mypy_verifier = MypyVerifier(timeout=10)
        self.pytest_verifier = PytestVerifier(timeout=120)

    def solve_task(self, task_prompt: str, test_code: str, entry_point: str) -> Dict:
        """Solve task with simultaneous feedback"""
        iteration = 0
        prompt = task_prompt
        total_tokens = 0
        mypy_tokens_total = 0
        pytest_tokens_total = 0

        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"AGGREGATION iteration {iteration}/{self.max_iterations}")

            # Generate code
            code = self.generator.generate(prompt)

            # Run both verifiers (always)
            mypy_result = self.mypy_verifier.verify(code)
            pytest_result = self.pytest_verifier.verify(code, test_code, entry_point)

            # Format feedback
            mypy_feedback = self.mypy_verifier.format_feedback(mypy_result["stderr"])
            pytest_feedback = self.pytest_verifier.format_feedback(pytest_result["stdout"])

            # Count tokens
            mypy_tokens = self.generator.count_tokens(mypy_feedback)
            pytest_tokens = self.generator.count_tokens(pytest_feedback)
            total_tokens += (mypy_tokens + pytest_tokens)
            mypy_tokens_total += mypy_tokens
            pytest_tokens_total += pytest_tokens

            # Check success
            if mypy_result["success"] and pytest_result["success"]:
                logger.info(f"AGGREGATION: Task solved in {iteration} iterations")
                return {
                    "code": code,
                    "iterations": iteration,
                    "total_tokens": total_tokens,
                    "mypy_tokens": mypy_tokens_total,
                    "pytest_tokens": pytest_tokens_total,
                    "success": True
                }

            # Combine feedback
            combined_feedback = f"{mypy_feedback}\n\n{pytest_feedback}"
            prompt = prompt + f"\n\nIteration {iteration} - Feedback:\n{combined_feedback}\n\nPlease fix the code."

        # Max iterations reached
        logger.warning(f"AGGREGATION: Max iterations reached without success")
        return {
            "code": code,
            "iterations": self.max_iterations,
            "total_tokens": total_tokens,
            "mypy_tokens": mypy_tokens_total,
            "pytest_tokens": pytest_tokens_total,
            "success": False
        }


class TokenEfficiencyAnalyzer:
    """Compute token efficiency metrics"""

    def __init__(self, threshold: float = 1.15):
        self.threshold = threshold

    def compute_tokens_per_task(self, results: List[Dict]) -> Dict:
        """Compute primary metric: tokens per successful task"""
        successful = [r for r in results if r["success"]]

        if not successful:
            logger.warning("No successful tasks!")
            return {
                "tokens_per_task": float('inf'),
                "successful_tasks": 0,
                "total_tokens": 0,
                "mean_iterations": 0
            }

        total_tokens = sum(r["total_tokens"] for r in successful)
        tokens_per_task = total_tokens / len(successful)
        mean_iterations = sum(r["iterations"] for r in successful) / len(successful)

        return {
            "tokens_per_task": tokens_per_task,
            "successful_tasks": len(successful),
            "total_tokens": total_tokens,
            "mean_iterations": mean_iterations
        }

    def compute_efficiency_ratio(self, cascade_metrics: Dict, aggregation_metrics: Dict) -> float:
        """Compute CASCADE / AGGREGATION ratio"""
        return cascade_metrics["tokens_per_task"] / aggregation_metrics["tokens_per_task"]

    def validate_gate(self, ratio: float) -> bool:
        """Check if ratio ≤ threshold"""
        return ratio <= self.threshold

    def compute_secondary_metrics(self, cascade_results: List, aggregation_results: List) -> Dict:
        """Compute exploratory metrics"""
        # Gating efficiency
        total_cascade_iterations = sum(r["iterations"] for r in cascade_results)
        gating_skipped = sum(r.get("gating_skipped_count", 0) for r in cascade_results)
        gating_efficiency = (gating_skipped / total_cascade_iterations * 100) if total_cascade_iterations > 0 else 0

        # Token breakdown
        cascade_mypy = sum(r["mypy_tokens"] for r in cascade_results)
        cascade_pytest = sum(r["pytest_tokens"] for r in cascade_results)
        aggregation_mypy = sum(r["mypy_tokens"] for r in aggregation_results)
        aggregation_pytest = sum(r["pytest_tokens"] for r in aggregation_results)

        # Success rates
        cascade_success_rate = sum(r["success"] for r in cascade_results) / len(cascade_results)
        aggregation_success_rate = sum(r["success"] for r in aggregation_results) / len(aggregation_results)

        return {
            "gating_efficiency_pct": gating_efficiency,
            "cascade_token_breakdown": {"mypy": cascade_mypy, "pytest": cascade_pytest},
            "aggregation_token_breakdown": {"mypy": aggregation_mypy, "pytest": aggregation_pytest},
            "success_rates": {"cascade": cascade_success_rate, "aggregation": aggregation_success_rate}
        }


class ExperimentVisualizer:
    """Generate experiment figures"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_style("whitegrid")

    def plot_gate_metrics(self, target: float, actual: float, passed: bool) -> None:
        """Gate validation figure"""
        fig, ax = plt.subplots(figsize=(8, 6))

        x = ['Target\n(≤1.15)', 'Actual\nRatio']
        y = [target, actual]
        colors = ['green', 'green' if passed else 'red']

        ax.bar(x, y, color=colors, alpha=0.7)
        ax.axhline(y=1.15, color='red', linestyle='--', label='Threshold (1.15)')
        ax.set_ylabel('Ratio')
        ax.set_title('Gate Validation: Token Efficiency Ratio')
        ax.legend()

        plt.tight_layout()
        plt.savefig(self.output_dir / 'gate_metrics.png', dpi=300)
        plt.close()
        logger.info("Generated gate_metrics.png")

    def plot_token_efficiency_comparison(self, cascade_metrics: Dict, aggregation_metrics: Dict) -> None:
        """Bar chart: CASCADE vs AGGREGATION tokens-per-task"""
        fig, ax = plt.subplots(figsize=(8, 6))

        x = ['CASCADE', 'AGGREGATION']
        y = [cascade_metrics["tokens_per_task"], aggregation_metrics["tokens_per_task"]]

        ax.bar(x, y, color=['blue', 'orange'], alpha=0.7)
        ax.set_ylabel('Tokens per Successful Task')
        ax.set_title('Token Efficiency Comparison')
        ax.axhline(y=aggregation_metrics["tokens_per_task"] * 1.15, color='red',
                   linestyle='--', label='15% overhead threshold')
        ax.legend()

        plt.tight_layout()
        plt.savefig(self.output_dir / 'token_efficiency.png', dpi=300)
        plt.close()
        logger.info("Generated token_efficiency.png")

    def plot_token_breakdown(self, cascade_results: List, aggregation_results: List) -> None:
        """Stacked bar: mypy vs pytest token contribution"""
        fig, ax = plt.subplots(figsize=(10, 6))

        cascade_mypy = sum(r["mypy_tokens"] for r in cascade_results)
        cascade_pytest = sum(r["pytest_tokens"] for r in cascade_results)
        agg_mypy = sum(r["mypy_tokens"] for r in aggregation_results)
        agg_pytest = sum(r["pytest_tokens"] for r in aggregation_results)

        x = ['CASCADE', 'AGGREGATION']
        mypy_tokens = [cascade_mypy, agg_mypy]
        pytest_tokens = [cascade_pytest, agg_pytest]

        ax.bar(x, mypy_tokens, label='Mypy tokens', color='steelblue')
        ax.bar(x, pytest_tokens, bottom=mypy_tokens, label='Pytest tokens', color='coral')

        ax.set_ylabel('Total Tokens')
        ax.set_title('Token Breakdown by Source')
        ax.legend()

        plt.tight_layout()
        plt.savefig(self.output_dir / 'token_breakdown.png', dpi=300)
        plt.close()
        logger.info("Generated token_breakdown.png")

    def plot_gating_efficiency(self, cascade_results: List) -> None:
        """Histogram: % execution skipped in CASCADE"""
        fig, ax = plt.subplots(figsize=(8, 6))

        efficiencies = []
        for r in cascade_results:
            if r["iterations"] > 0:
                eff = (r.get("gating_skipped_count", 0) / r["iterations"]) * 100
                efficiencies.append(eff)

        ax.hist(efficiencies, bins=10, color='green', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Gating Efficiency (%)')
        ax.set_ylabel('Number of Tasks')
        ax.set_title('Distribution of Execution Skipping in CASCADE')
        ax.axvline(x=np.mean(efficiencies), color='red', linestyle='--',
                   label=f'Mean: {np.mean(efficiencies):.1f}%')
        ax.legend()

        plt.tight_layout()
        plt.savefig(self.output_dir / 'gating_efficiency.png', dpi=300)
        plt.close()
        logger.info("Generated gating_efficiency.png")

    def plot_iterations_comparison(self, cascade_results: List, aggregation_results: List) -> None:
        """Box plot: convergence iterations both conditions"""
        fig, ax = plt.subplots(figsize=(8, 6))

        cascade_iters = [r["iterations"] for r in cascade_results if r["success"]]
        agg_iters = [r["iterations"] for r in aggregation_results if r["success"]]

        data = [cascade_iters, agg_iters]
        ax.boxplot(data, labels=['CASCADE', 'AGGREGATION'])
        ax.set_ylabel('Iterations to Solution')
        ax.set_title('Convergence Speed Comparison')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'iterations_comparison.png', dpi=300)
        plt.close()
        logger.info("Generated iterations_comparison.png")


class TokenEfficiencyPipeline:
    """Main experiment pipeline orchestrator"""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.loader = HumanEvalLoader(use_evalplus=True)
        self.generator = None
        self.cascade_router = None
        self.aggregation_router = None
        self.analyzer = TokenEfficiencyAnalyzer(threshold=config.efficiency_threshold)
        self.visualizer = ExperimentVisualizer(config.figures_dir)

        # Create output directories
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.figures_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> Dict:
        """Execute full pipeline"""
        logger.info("Starting H-M3 Token Efficiency Pipeline")

        # Stage 1: Load qualified tasks
        logger.info("Stage 1: Loading qualified tasks")
        qualified_tasks = self.stage_load_qualified_tasks()
        logger.info(f"Loaded {len(qualified_tasks)} qualified tasks")

        # Initialize model and routers
        logger.info("Initializing CodeLlama-7B model...")
        self.generator = CodeLlamaGenerator(self.config)
        self.generator.load_model()

        self.cascade_router = CascadeRouter(self.generator, self.config.max_iterations)
        self.aggregation_router = AggregationRouter(self.generator, self.config.max_iterations)

        # Stage 2: CASCADE evaluation
        logger.info("Stage 2: CASCADE evaluation")
        cascade_results = self.stage_cascade_evaluation(qualified_tasks)
        self.save_results(cascade_results, self.config.output_dir / "cascade_results.jsonl")

        # Stage 3: AGGREGATION evaluation
        logger.info("Stage 3: AGGREGATION evaluation")
        aggregation_results = self.stage_aggregation_evaluation(qualified_tasks)
        self.save_results(aggregation_results, self.config.output_dir / "aggregation_results.jsonl")

        # Stage 4: Analyze efficiency
        logger.info("Stage 4: Analyzing token efficiency")
        metrics = self.stage_analyze_efficiency(cascade_results, aggregation_results)

        # Stage 5: Generate visualizations
        logger.info("Stage 5: Generating visualizations")
        self.stage_generate_visualizations(cascade_results, aggregation_results, metrics)

        # Stage 6: Validate gate
        logger.info("Stage 6: Validating gate")
        gate_result = self.stage_validate_gate(metrics)

        # Save final results
        final_results = {
            "cascade_results": cascade_results,
            "aggregation_results": aggregation_results,
            "metrics": metrics,
            "gate_satisfied": gate_result["gate_satisfied"],
            "gate_type": "SHOULD_WORK"
        }
        self.save_results(final_results, self.config.output_dir / "experiment_results.json")

        logger.info("Pipeline completed successfully")
        return final_results

    def stage_load_qualified_tasks(self) -> Dict[str, Dict]:
        """Stage 1: Load N=20 dual-sensitive tasks"""
        all_problems = self.loader.load_problems()
        qualified_ids = self.loader.load_qualified_task_ids(self.config.h_e1_validation_path)

        qualified_tasks = {}
        for task_id in qualified_ids:
            if task_id in all_problems:
                qualified_tasks[task_id] = all_problems[task_id]
            else:
                logger.warning(f"Task {task_id} not found in dataset")

        logger.info(f"Successfully loaded {len(qualified_tasks)} qualified tasks")
        return qualified_tasks

    def stage_cascade_evaluation(self, tasks: Dict) -> List[Dict]:
        """Stage 2: Evaluate with CASCADE router"""
        results = []

        for i, (task_id, problem) in enumerate(tasks.items(), 1):
            logger.info(f"CASCADE: Evaluating task {i}/{len(tasks)}: {task_id}")

            task_prompt = problem["prompt"]
            test_code = problem.get("test", "")
            entry_point = problem.get("entry_point", "")

            result = self.cascade_router.solve_task(task_prompt, test_code, entry_point)
            result["task_id"] = task_id
            results.append(result)

            # Checkpoint every 5 tasks
            if i % 5 == 0:
                self.save_results(results, self.config.output_dir / "cascade_results_checkpoint.jsonl")

        return results

    def stage_aggregation_evaluation(self, tasks: Dict) -> List[Dict]:
        """Stage 3: Evaluate with AGGREGATION router"""
        results = []

        for i, (task_id, problem) in enumerate(tasks.items(), 1):
            logger.info(f"AGGREGATION: Evaluating task {i}/{len(tasks)}: {task_id}")

            task_prompt = problem["prompt"]
            test_code = problem.get("test", "")
            entry_point = problem.get("entry_point", "")

            result = self.aggregation_router.solve_task(task_prompt, test_code, entry_point)
            result["task_id"] = task_id
            results.append(result)

            # Checkpoint every 5 tasks
            if i % 5 == 0:
                self.save_results(results, self.config.output_dir / "aggregation_results_checkpoint.jsonl")

        return results

    def stage_analyze_efficiency(self, cascade_results: List, aggregation_results: List) -> Dict:
        """Stage 4: Compute token efficiency metrics"""
        cascade_metrics = self.analyzer.compute_tokens_per_task(cascade_results)
        aggregation_metrics = self.analyzer.compute_tokens_per_task(aggregation_results)

        efficiency_ratio = self.analyzer.compute_efficiency_ratio(cascade_metrics, aggregation_metrics)
        secondary_metrics = self.analyzer.compute_secondary_metrics(cascade_results, aggregation_results)

        metrics = {
            "cascade": cascade_metrics,
            "aggregation": aggregation_metrics,
            "efficiency_ratio": efficiency_ratio,
            "secondary": secondary_metrics
        }

        logger.info(f"CASCADE tokens/task: {cascade_metrics['tokens_per_task']:.2f}")
        logger.info(f"AGGREGATION tokens/task: {aggregation_metrics['tokens_per_task']:.2f}")
        logger.info(f"Efficiency ratio: {efficiency_ratio:.3f}")

        return metrics

    def stage_generate_visualizations(self, cascade_results: List, aggregation_results: List, metrics: Dict) -> None:
        """Stage 5: Generate 5 figures"""
        ratio = metrics["efficiency_ratio"]
        passed = self.analyzer.validate_gate(ratio)

        self.visualizer.plot_gate_metrics(1.15, ratio, passed)
        self.visualizer.plot_token_efficiency_comparison(metrics["cascade"], metrics["aggregation"])
        self.visualizer.plot_token_breakdown(cascade_results, aggregation_results)
        self.visualizer.plot_gating_efficiency(cascade_results)
        self.visualizer.plot_iterations_comparison(cascade_results, aggregation_results)

    def stage_validate_gate(self, metrics: Dict) -> Dict:
        """Stage 6: Validate ≤1.15 gate"""
        ratio = metrics["efficiency_ratio"]
        gate_satisfied = self.analyzer.validate_gate(ratio)

        result = {
            "gate_type": "SHOULD_WORK",
            "gate_satisfied": gate_satisfied,
            "efficiency_ratio": ratio,
            "threshold": self.config.efficiency_threshold
        }

        if gate_satisfied:
            logger.info(f"✅ GATE PASSED: Ratio {ratio:.3f} ≤ {self.config.efficiency_threshold}")
        else:
            logger.warning(f"⚠️ GATE FAILED: Ratio {ratio:.3f} > {self.config.efficiency_threshold}")
            logger.warning("SHOULD_WORK gate failure will be documented as limitation")

        return result

    def save_results(self, results: any, path: Path) -> None:
        """Save results to JSON"""
        with open(path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved results to {path}")


def main():
    """Entry point"""
    config = ExperimentConfig()
    pipeline = TokenEfficiencyPipeline(config)

    try:
        results = pipeline.run()
        print(f"\n{'='*60}")
        print(f"EXPERIMENT COMPLETED")
        print(f"{'='*60}")
        print(f"Gate status: {'PASSED' if results['gate_satisfied'] else 'FAILED (documented as limitation)'}")
        print(f"Efficiency ratio: {results['metrics']['efficiency_ratio']:.3f}")
        print(f"{'='*60}\n")

        return 0 if results['gate_satisfied'] else 1

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
