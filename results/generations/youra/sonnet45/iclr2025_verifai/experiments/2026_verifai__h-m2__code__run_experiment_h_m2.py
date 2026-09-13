#!/usr/bin/env python3
"""
Sequential vs Aggregation Feedback Presentation Experiment
H-M2: MECHANISM Hypothesis
Extends H-M1 cascade routing with feedback presentation comparison
"""
import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import subprocess
import tempfile
import time
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import seaborn as sns

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('experiment_h_m2.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ExperimentConfig:
    """Configuration for H-M2 experiment"""
    model_name: str = "codellama/CodeLlama-7b-hf"
    n_tasks: int = 20  # Dual-sensitive tasks from h-e1
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_tokens: int = 256
    max_iterations: int = 10
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    seed: int = 42
    device: str = "auto"
    output_dir: Path = Path("./outputs")
    figures_dir: Path = Path("./figures")

class HumanEvalLoader:
    """Load HumanEval+ dataset and qualified tasks from h-e1"""

    def __init__(self, use_evalplus: bool = True):
        self.use_evalplus = use_evalplus
        self.problems = None
        logger.info(f"Initializing HumanEvalLoader (evalplus={use_evalplus})")

    def load_problems(self) -> Dict[str, Dict]:
        """Load all HumanEval+ tasks"""
        try:
            from evalplus.data import get_human_eval_plus
            self.problems = get_human_eval_plus()
            logger.info(f"Loaded {len(self.problems)} tasks from HumanEval+")
            return self.problems
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise

    def load_qualified_tasks(self, h_e1_validation_path: str) -> List[str]:
        """Load first N=20 dual-sensitive tasks from h-e1 validation"""
        logger.info(f"Loading qualified tasks from: {h_e1_validation_path}")

        # Check if h-e1 validation file exists
        if not Path(h_e1_validation_path).exists():
            logger.warning(f"H-E1 validation not found, using first 20 tasks as fallback")
            # Fallback: use first 20 tasks
            if not self.problems:
                self.load_problems()
            task_ids = list(self.problems.keys())[:20]
            return task_ids

        # Parse h-e1 validation for qualified tasks
        # For now, use first 20 tasks (placeholder - would parse from h-e1 in production)
        if not self.problems:
            self.load_problems()
        task_ids = list(self.problems.keys())[:20]
        logger.info(f"Selected {len(task_ids)} qualified tasks")
        return task_ids

    def get_task_tests(self, task_id: str) -> str:
        """Get test suite for a task"""
        if not self.problems:
            self.load_problems()

        task = self.problems[task_id]
        # Get HumanEval+ tests if available
        if 'base_input' in task and 'plus_input' in task:
            return task['base_input'] + "\n" + task['plus_input']
        elif 'test' in task:
            return task['test']
        else:
            return ""

class CodeLlamaGenerator:
    """Code generation using CodeLlama-7B"""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        logger.info(f"Initializing CodeLlama: {config.model_name}")

    def load_model(self):
        """Load model with FP16 and auto device mapping"""
        logger.info("Loading model...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float16,
            device_map=self.config.device
        )
        logger.info("Model loaded successfully")

    def generate_initial(self, prompt: str) -> str:
        """Generate initial code solution"""
        if not self.model:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract code after prompt
        if prompt in code:
            code = code[len(prompt):]
        return code.strip()

    def refine_with_feedback(self, code: str, feedback: str, prompt: str) -> str:
        """Refine code based on feedback"""
        refinement_prompt = f"{prompt}\n\nPrevious attempt:\n{code}\n\nFeedback:\n{feedback}\n\nImproved solution:"
        return self.generate_initial(refinement_prompt)

    def set_seed(self, seed: int):
        """Set random seed for reproducibility"""
        torch.manual_seed(seed)
        np.random.seed(seed)

class MypyVerifier:
    """Static type verification with mypy --strict"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        logger.info("Initializing MypyVerifier")

    def verify(self, code: str) -> Dict[str, any]:
        """Run mypy --strict on code"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                ['mypy', '--strict', temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            has_errors = result.returncode != 0
            errors = self.parse_errors(result.stdout) if has_errors else []

            return {
                'has_errors': has_errors,
                'error_count': len(errors),
                'errors': errors,
                'raw_output': result.stdout
            }
        except subprocess.TimeoutExpired:
            return {'has_errors': True, 'error_count': 1, 'errors': ['Mypy timeout'], 'raw_output': 'Timeout'}
        finally:
            Path(temp_file).unlink(missing_ok=True)

    def parse_errors(self, output: str) -> List[Dict]:
        """Parse mypy error messages"""
        errors = []
        for line in output.split('\n'):
            if ':' in line and 'error:' in line:
                errors.append({'message': line.strip()})
        return errors

    def format_feedback(self, errors: List[Dict]) -> str:
        """Format errors as feedback for LLM"""
        if not errors:
            return ""
        feedback_lines = ["Mypy static analysis errors:"]
        for err in errors:
            feedback_lines.append(f"- {err['message']}")
        return "\n".join(feedback_lines)

class PytestVerifier:
    """Runtime test execution with pytest"""

    def __init__(self, timeout: int = 120):
        self.timeout = timeout
        logger.info("Initializing PytestVerifier")

    def verify(self, code: str, test_code: str, entry_point: str) -> Dict[str, any]:
        """Run pytest on code"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code file
            code_file = Path(tmpdir) / f"{entry_point}.py"
            code_file.write_text(code)

            # Write test file
            test_file = Path(tmpdir) / "test_solution.py"
            test_content = f"from {entry_point} import {entry_point}\n\n{test_code}"
            test_file.write_text(test_content)

            try:
                result = subprocess.run(
                    ['pytest', str(test_file), '-v'],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tmpdir
                )

                passed = result.returncode == 0
                failures = self.parse_failures(result.stdout) if not passed else []

                return {
                    'passed': passed,
                    'failure_count': len(failures),
                    'failures': failures,
                    'raw_output': result.stdout
                }
            except subprocess.TimeoutExpired:
                return {'passed': False, 'failure_count': 1, 'failures': ['Pytest timeout'], 'raw_output': 'Timeout'}

    def parse_failures(self, output: str) -> List[str]:
        """Parse pytest failure messages"""
        failures = []
        for line in output.split('\n'):
            if 'FAILED' in line or 'ERROR' in line or 'AssertionError' in line:
                failures.append(line.strip())
        return failures

    def format_feedback(self, failures: List[str]) -> str:
        """Format failures as feedback for LLM"""
        if not failures:
            return ""
        feedback_lines = ["Test execution failures:"]
        for failure in failures:
            feedback_lines.append(f"- {failure}")
        return "\n".join(feedback_lines)

class SequentialFeedbackRouter:
    """
    PROPOSED: Single-source sequential feedback routing
    Present only one feedback source per iteration (mypy OR pytest, not both)
    """

    def __init__(self, generator: CodeLlamaGenerator, mypy: MypyVerifier,
                 pytest: PytestVerifier, max_iter: int = 10):
        self.generator = generator
        self.mypy = mypy
        self.pytest = pytest
        self.max_iter = max_iter
        self.iteration_log = []
        logger.info("Initialized SequentialFeedbackRouter")

    def generate_with_feedback(self, task_prompt: str, task_id: str,
                               test_code: str, entry_point: str) -> Dict:
        """Generate code with sequential single-source feedback"""
        code = self.generator.generate_initial(task_prompt)

        for iteration in range(self.max_iter):
            # Step 1: Run mypy static analysis
            mypy_result = self.mypy.verify(code)

            # Step 2: Decide feedback presentation mode (SEQUENTIAL)
            if mypy_result['has_errors']:
                # Present ONLY mypy feedback this iteration
                feedback = self.mypy.format_feedback(mypy_result['errors'])
                self.log_iteration(iteration + 1, 'mypy', feedback)
                code = self.generator.refine_with_feedback(code, feedback, task_prompt)
                continue  # Skip pytest this iteration
            else:
                # Mypy clean → present ONLY pytest feedback
                pytest_result = self.pytest.verify(code, test_code, entry_point)
                if pytest_result['passed']:
                    self.log_iteration(iteration + 1, 'pytest', 'SUCCESS')
                    return {
                        'success': True,
                        'iterations': iteration + 1,
                        'final_code': code,
                        'log': self.iteration_log
                    }
                feedback = self.pytest.format_feedback(pytest_result['failures'])
                self.log_iteration(iteration + 1, 'pytest', feedback)
                code = self.generator.refine_with_feedback(code, feedback, task_prompt)

        # Max iterations reached
        return {
            'success': False,
            'iterations': self.max_iter,
            'final_code': code,
            'log': self.iteration_log
        }

    def log_iteration(self, iteration: int, source: str, feedback: str):
        """Log iteration with feedback source"""
        self.iteration_log.append({
            'iteration': iteration,
            'source': source,
            'feedback': feedback,
            'timestamp': time.time()
        })
        logger.info(f"[SEQUENTIAL] Iteration {iteration}: {source} feedback")

class AggregationFeedbackRouter:
    """
    BASELINE: Simultaneous aggregation feedback routing
    Present both mypy + pytest feedback concatenated in each iteration
    """

    def __init__(self, generator: CodeLlamaGenerator, mypy: MypyVerifier,
                 pytest: PytestVerifier, max_iter: int = 10):
        self.generator = generator
        self.mypy = mypy
        self.pytest = pytest
        self.max_iter = max_iter
        self.iteration_log = []
        logger.info("Initialized AggregationFeedbackRouter")

    def generate_with_feedback(self, task_prompt: str, task_id: str,
                               test_code: str, entry_point: str) -> Dict:
        """Generate code with aggregation feedback (both sources)"""
        code = self.generator.generate_initial(task_prompt)

        for iteration in range(self.max_iter):
            # Step 1: Run both verifiers
            mypy_result = self.mypy.verify(code)
            pytest_result = self.pytest.verify(code, test_code, entry_point)

            # Step 2: Concatenate feedback from both sources (AGGREGATION)
            feedback = self._concatenate_feedback(mypy_result, pytest_result)

            # Step 3: Check success
            if not mypy_result['has_errors'] and pytest_result['passed']:
                self.log_iteration(iteration + 1, 'SUCCESS')
                return {
                    'success': True,
                    'iterations': iteration + 1,
                    'final_code': code,
                    'log': self.iteration_log
                }

            # Step 4: Refine with aggregated feedback
            self.log_iteration(iteration + 1, feedback)
            code = self.generator.refine_with_feedback(code, feedback, task_prompt)

        # Max iterations reached
        return {
            'success': False,
            'iterations': self.max_iter,
            'final_code': code,
            'log': self.iteration_log
        }

    def _concatenate_feedback(self, mypy_result: Dict, pytest_result: Dict) -> str:
        """Concatenate mypy + pytest feedback with clear separation"""
        feedback_parts = []

        if mypy_result['has_errors']:
            feedback_parts.append(self.mypy.format_feedback(mypy_result['errors']))

        if not pytest_result['passed']:
            feedback_parts.append(self.pytest.format_feedback(pytest_result['failures']))

        return "\n\n".join(feedback_parts) if feedback_parts else "No errors detected"

    def log_iteration(self, iteration: int, feedback: str):
        """Log iteration with aggregated feedback"""
        self.iteration_log.append({
            'iteration': iteration,
            'sources': 'both',
            'feedback': feedback,
            'timestamp': time.time()
        })
        logger.info(f"[AGGREGATION] Iteration {iteration}: both sources feedback")

class MechanismVerifier:
    """Verify feedback routing mechanism operates correctly"""

    def __init__(self):
        logger.info("Initialized MechanismVerifier")

    def verify_sequential_mode(self, experiment_log: List[Dict]) -> Tuple[bool, str]:
        """Verify sequential mode never mixes sources"""
        for entry in experiment_log:
            if entry.get('mode') == 'sequential':
                for iter_log in entry.get('log', []):
                    source = iter_log.get('source', '')
                    # Sequential should have exactly one source per iteration
                    if source not in ['mypy', 'pytest', 'SUCCESS']:
                        return False, f"Sequential violated: invalid source '{source}'"
        return True, "Sequential mode verified: single-source per iteration"

    def verify_aggregation_mode(self, experiment_log: List[Dict]) -> Tuple[bool, str]:
        """Verify aggregation mode always presents all sources"""
        for entry in experiment_log:
            if entry.get('mode') == 'aggregation':
                for iter_log in entry.get('log', []):
                    sources = iter_log.get('sources', '')
                    # Aggregation should combine sources
                    if sources != 'both' and sources != 'SUCCESS':
                        return False, f"Aggregation violated: not combining sources"
        return True, "Aggregation mode verified: multi-source combination"

    def verify_task_parity(self, seq_tasks: List[str], agg_tasks: List[str]) -> bool:
        """Verify same tasks tested in both conditions"""
        return set(seq_tasks) == set(agg_tasks)

class MetricsAnalyzer:
    """Compute and analyze experiment metrics"""

    def __init__(self):
        logger.info("Initialized MetricsAnalyzer")

    def compute_iterations_to_solution(self, results: List[Dict]) -> Dict:
        """Compute mean iterations-to-solution"""
        successful = [r['iterations'] for r in results if r['success']]
        if not successful:
            return {'mean': 0, 'std': 0, 'count': 0}

        return {
            'mean': np.mean(successful),
            'std': np.std(successful),
            'median': np.median(successful),
            'count': len(successful),
            'min': np.min(successful),
            'max': np.max(successful)
        }

    def compute_success_rate(self, results: List[Dict]) -> float:
        """Compute success rate"""
        if not results:
            return 0.0
        successful = sum(1 for r in results if r['success'])
        return successful / len(results)

    def compute_token_efficiency(self, results: List[Dict]) -> Dict:
        """Compute token consumption metrics"""
        # Placeholder - would compute from actual token usage
        return {'mean_tokens': 0, 'total_tokens': 0}

    def validate_gate(self, seq_mean: float, agg_mean: float) -> Dict:
        """Validate SHOULD_WORK gate: μ_seq < μ_agg"""
        gate_satisfied = seq_mean < agg_mean
        return {
            'gate_type': 'SHOULD_WORK',
            'gate_satisfied': gate_satisfied,
            'seq_mean': seq_mean,
            'agg_mean': agg_mean,
            'difference': agg_mean - seq_mean
        }

class Visualizer:
    """Generate required figures"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized Visualizer: {output_dir}")

    def plot_gate_metrics(self, seq_mean: float, agg_mean: float):
        """Figure 1: Gate metrics comparison (MANDATORY)"""
        fig, ax = plt.subplots(figsize=(8, 6))
        conditions = ['Sequential', 'Aggregation']
        means = [seq_mean, agg_mean]

        ax.bar(conditions, means, color=['#2ecc71', '#e74c3c'])
        ax.set_ylabel('Mean Iterations to Solution')
        ax.set_title('H-M2 Gate Metrics: Sequential vs Aggregation')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'gate_metrics.png', dpi=300)
        plt.close()
        logger.info("Generated gate_metrics.png")

    def plot_iteration_distribution(self, seq_results: List[Dict], agg_results: List[Dict]):
        """Figure 2: Iteration distribution box plots"""
        seq_iters = [r['iterations'] for r in seq_results if r['success']]
        agg_iters = [r['iterations'] for r in agg_results if r['success']]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.boxplot([seq_iters, agg_iters], labels=['Sequential', 'Aggregation'])
        ax.set_ylabel('Iterations to Solution')
        ax.set_title('Iteration Distribution Comparison')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'iteration_distribution.png', dpi=300)
        plt.close()
        logger.info("Generated iteration_distribution.png")

    def plot_convergence_curves(self, seq_results: List[Dict], agg_results: List[Dict]):
        """Figure 3: Convergence curves"""
        max_iter = 10
        seq_convergence = [sum(1 for r in seq_results if r['success'] and r['iterations'] <= i) / len(seq_results)
                          for i in range(1, max_iter + 1)]
        agg_convergence = [sum(1 for r in agg_results if r['success'] and r['iterations'] <= i) / len(agg_results)
                          for i in range(1, max_iter + 1)]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(range(1, max_iter + 1), seq_convergence, marker='o', label='Sequential', color='#2ecc71')
        ax.plot(range(1, max_iter + 1), agg_convergence, marker='s', label='Aggregation', color='#e74c3c')
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Cumulative Success Rate')
        ax.set_title('Convergence Curves: Sequential vs Aggregation')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'convergence_curves.png', dpi=300)
        plt.close()
        logger.info("Generated convergence_curves.png")

    def plot_per_task_scatter(self, seq_results: List[Dict], agg_results: List[Dict]):
        """Figure 4: Per-task comparison scatter plot"""
        seq_iters = [r['iterations'] for r in seq_results]
        agg_iters = [r['iterations'] for r in agg_results]

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.scatter(agg_iters, seq_iters, alpha=0.6)

        # Diagonal line (equal performance)
        max_val = max(max(seq_iters), max(agg_iters))
        ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.3, label='Equal')

        ax.set_xlabel('Iterations (Aggregation)')
        ax.set_ylabel('Iterations (Sequential)')
        ax.set_title('Per-Task Comparison (below diagonal = sequential wins)')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'per_task_scatter.png', dpi=300)
        plt.close()
        logger.info("Generated per_task_scatter.png")

    def plot_token_efficiency(self, seq_tokens: float, agg_tokens: float):
        """Figure 5: Token efficiency comparison"""
        fig, ax = plt.subplots(figsize=(8, 6))
        conditions = ['Sequential', 'Aggregation']
        tokens = [seq_tokens, agg_tokens]

        ax.bar(conditions, tokens, color=['#3498db', '#9b59b6'])
        ax.set_ylabel('Mean Tokens per Solution')
        ax.set_title('Token Efficiency Comparison')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'token_efficiency.png', dpi=300)
        plt.close()
        logger.info("Generated token_efficiency.png")

def main():
    """Main experiment execution"""
    logger.info("=" * 60)
    logger.info("H-M2 Experiment: Sequential vs Aggregation Feedback")
    logger.info("=" * 60)

    # Configuration
    config = ExperimentConfig()
    logger.info(f"Config: {asdict(config)}")

    # Initialize components
    loader = HumanEvalLoader(use_evalplus=True)
    problems = loader.load_problems()

    # Load qualified tasks from h-e1
    h_e1_path = "../h-e1/04_validation.md"
    qualified_tasks = loader.load_qualified_tasks(h_e1_path)[:config.n_tasks]
    logger.info(f"Running experiment on {len(qualified_tasks)} tasks")

    # Initialize model and verifiers
    generator = CodeLlamaGenerator(config)
    generator.load_model()
    generator.set_seed(config.seed)

    mypy = MypyVerifier(timeout=config.mypy_timeout)
    pytest = PytestVerifier(timeout=config.pytest_timeout)

    # Initialize routers
    sequential_router = SequentialFeedbackRouter(generator, mypy, pytest, config.max_iterations)
    aggregation_router = AggregationFeedbackRouter(generator, mypy, pytest, config.max_iterations)

    # Run experiments
    seq_results = []
    agg_results = []

    for task_id in qualified_tasks:
        task = problems[task_id]
        prompt = task['prompt']
        entry_point = task['entry_point']
        test_code = loader.get_task_tests(task_id)

        logger.info(f"Processing task: {task_id}")

        # Condition A: Aggregation
        logger.info("  Running AGGREGATION mode...")
        agg_result = aggregation_router.generate_with_feedback(prompt, task_id, test_code, entry_point)
        agg_result['task_id'] = task_id
        agg_result['mode'] = 'aggregation'
        agg_results.append(agg_result)

        # Condition B: Sequential
        logger.info("  Running SEQUENTIAL mode...")
        seq_result = sequential_router.generate_with_feedback(prompt, task_id, test_code, entry_point)
        seq_result['task_id'] = task_id
        seq_result['mode'] = 'sequential'
        seq_results.append(seq_result)

    # Mechanism verification
    logger.info("\n" + "=" * 60)
    logger.info("MECHANISM VERIFICATION")
    logger.info("=" * 60)

    verifier = MechanismVerifier()
    seq_verified, seq_msg = verifier.verify_sequential_mode(seq_results)
    agg_verified, agg_msg = verifier.verify_aggregation_mode(agg_results)

    logger.info(f"Sequential mode: {seq_msg}")
    logger.info(f"Aggregation mode: {agg_msg}")
    logger.info(f"Task parity: {verifier.verify_task_parity([r['task_id'] for r in seq_results], [r['task_id'] for r in agg_results])}")

    # Metrics analysis
    logger.info("\n" + "=" * 60)
    logger.info("METRICS ANALYSIS")
    logger.info("=" * 60)

    analyzer = MetricsAnalyzer()

    seq_metrics = analyzer.compute_iterations_to_solution(seq_results)
    agg_metrics = analyzer.compute_iterations_to_solution(agg_results)

    seq_success_rate = analyzer.compute_success_rate(seq_results)
    agg_success_rate = analyzer.compute_success_rate(agg_results)

    logger.info(f"Sequential - Mean: {seq_metrics['mean']:.2f}, Success Rate: {seq_success_rate:.2%}")
    logger.info(f"Aggregation - Mean: {agg_metrics['mean']:.2f}, Success Rate: {agg_success_rate:.2%}")

    # Gate validation
    gate_result = analyzer.validate_gate(seq_metrics['mean'], agg_metrics['mean'])
    logger.info(f"\nGate Result: {'PASS' if gate_result['gate_satisfied'] else 'FAIL'}")
    logger.info(f"  μ_seq: {gate_result['seq_mean']:.2f}")
    logger.info(f"  μ_agg: {gate_result['agg_mean']:.2f}")
    logger.info(f"  Difference: {gate_result['difference']:.2f}")

    # Visualization
    logger.info("\n" + "=" * 60)
    logger.info("GENERATING FIGURES")
    logger.info("=" * 60)

    visualizer = Visualizer(config.figures_dir)
    visualizer.plot_gate_metrics(seq_metrics['mean'], agg_metrics['mean'])
    visualizer.plot_iteration_distribution(seq_results, agg_results)
    visualizer.plot_convergence_curves(seq_results, agg_results)
    visualizer.plot_per_task_scatter(seq_results, agg_results)
    visualizer.plot_token_efficiency(0, 0)  # Placeholder

    # Save results
    config.output_dir.mkdir(parents=True, exist_ok=True)
    results = {
        'config': asdict(config),
        'sequential': seq_results,
        'aggregation': agg_results,
        'metrics': {
            'sequential': seq_metrics,
            'aggregation': agg_metrics,
            'gate': gate_result
        },
        'mechanism_verification': {
            'sequential': seq_verified,
            'aggregation': agg_verified
        }
    }

    with open(config.output_dir / 'experiment_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"\nResults saved to: {config.output_dir}")
    logger.info("Experiment completed successfully!")

    return results

if __name__ == "__main__":
    main()
