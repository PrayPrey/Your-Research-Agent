#!/usr/bin/env python3
"""
Dual-Sensitive Task Classification Experiment
H-E1: EXISTENCE Hypothesis
"""
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple
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
        logging.FileHandler('experiment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ExperimentConfig:
    """Configuration for H-E1 experiment"""
    model_name: str = "codellama/CodeLlama-7b-hf"
    k_samples: int = 20
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_length: int = 256
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    variance_threshold: float = 1.0
    target_n: int = 20
    seed: int = 42
    device: str = "auto"
    output_dir: Path = Path("./outputs")
    figures_dir: Path = Path("./figures")

class HumanEvalLoader:
    """Load HumanEval dataset"""

    def __init__(self, use_evalplus: bool = True):
        self.use_evalplus = use_evalplus
        self.problems = None
        logger.info(f"Initializing HumanEvalLoader (evalplus={use_evalplus})")

    def load_problems(self) -> Dict[str, Dict]:
        """Load all 164 HumanEval tasks"""
        try:
            if self.use_evalplus:
                from evalplus.data import get_human_eval_plus
                self.problems = get_human_eval_plus()
                logger.info(f"Loaded {len(self.problems)} tasks from HumanEval+")
            else:
                from human_eval.data import read_problems
                self.problems = read_problems()
                logger.info(f"Loaded {len(self.problems)} tasks from HumanEval")
            return self.problems
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            # Fallback to human-eval
            if self.use_evalplus:
                logger.info("Falling back to human-eval...")
                from human_eval.data import read_problems
                self.problems = read_problems()
                logger.info(f"Loaded {len(self.problems)} tasks from HumanEval (fallback)")
            return self.problems

class CodeLlamaGenerator:
    """Generate code samples using CodeLlama-7B"""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        logger.info(f"Initializing CodeLlama: {config.model_name}")

    def load_model(self):
        """Load model with FP16 and auto device mapping"""
        logger.info("Loading model...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float16,
            device_map=self.config.device
        )
        logger.info("Model loaded successfully")

    def generate_samples(self, prompt: str, k: int = None) -> List[str]:
        """Generate K samples for a prompt"""
        if k is None:
            k = self.config.k_samples

        samples = []
        for i in range(k):
            torch.manual_seed(self.config.seed + i)
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=self.config.max_length,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    top_k=self.config.top_k,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            completion = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            samples.append(completion)

        return samples

class MypyVerifier:
    """Static verification with mypy --strict"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def verify(self, code: str) -> bool:
        """Verify single code sample with mypy"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            result = subprocess.run(
                ['mypy', '--strict', temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            passed = (result.returncode == 0)
            return passed
        except subprocess.TimeoutExpired:
            logger.warning("Mypy timeout")
            return False
        except Exception as e:
            logger.error(f"Mypy error: {e}")
            return False
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def verify_batch(self, codes: List[str]) -> List[bool]:
        """Batch verify codes"""
        return [self.verify(code) for code in codes]

class PytestVerifier:
    """Execution verification with pytest"""

    def __init__(self, timeout: int = 120):
        self.timeout = timeout

    def verify(self, code: str, test_code: str) -> bool:
        """Verify code with pytest"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Write code
            code_file = tmpdir / 'solution.py'
            code_file.write_text(code)

            # Write test
            test_file = tmpdir / 'test_solution.py'
            test_file.write_text(test_code)

            try:
                result = subprocess.run(
                    ['pytest', str(test_file), '-v', '--tb=short'],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tmpdir
                )
                passed = (result.returncode == 0)
                return passed
            except subprocess.TimeoutExpired:
                logger.warning("Pytest timeout")
                return False
            except Exception as e:
                logger.error(f"Pytest error: {e}")
                return False

    def verify_batch(self, codes: List[str], tests: List[str]) -> List[bool]:
        """Batch verify codes"""
        return [self.verify(code, test) for code, test in zip(codes, tests)]

class DualSensitivityClassifier:
    """Classify tasks as dual-sensitive"""

    def __init__(self, k_samples: int = 20, variance_threshold: float = 1.0):
        self.k_samples = k_samples
        self.variance_threshold = variance_threshold

    def classify_task(self, task_id: str, mypy_results: List[bool], pytest_results: List[bool]) -> Dict:
        """Classify a single task"""
        # Count patterns
        mypy_fail_pytest_pass = sum([(not m) and p for m, p in zip(mypy_results, pytest_results)])
        mypy_pass_pytest_fail = sum([m and (not p) for m, p in zip(mypy_results, pytest_results)])

        # Check dual-sensitivity
        dual_sensitive = (mypy_fail_pytest_pass >= 1) and (mypy_pass_pytest_fail >= 1)

        # Compute variance
        variance = self.compute_variance(mypy_results, pytest_results)

        # Check qualification
        qualified = dual_sensitive and (variance <= self.variance_threshold)

        return {
            'task_id': task_id,
            'dual_sensitive': dual_sensitive,
            'qualified': qualified,
            'mypy_fail_pytest_pass': mypy_fail_pytest_pass,
            'mypy_pass_pytest_fail': mypy_pass_pytest_fail,
            'variance': variance,
            'mypy_results': mypy_results,
            'pytest_results': pytest_results
        }

    def compute_variance(self, mypy_results: List[bool], pytest_results: List[bool]) -> float:
        """Compute within-task variance"""
        # Convert to numeric
        scores = []
        for m, p in zip(mypy_results, pytest_results):
            if m and p:
                scores.append(1.0)  # Both pass
            elif (not m) and (not p):
                scores.append(0.0)  # Both fail
            else:
                scores.append(0.5)  # Mixed

        return float(np.std(scores))

def create_test_code(problem: Dict) -> str:
    """Create pytest test from HumanEval problem"""
    test_code = f"""
import sys
from solution import {problem['entry_point']}

{problem['test']}

check({problem['entry_point']})
"""
    return test_code

def run_experiment(config: ExperimentConfig):
    """Main experiment execution"""
    logger.info("=" * 80)
    logger.info("Starting H-E1 Dual-Sensitivity Classification Experiment")
    logger.info("=" * 80)

    # Create output directories
    config.output_dir.mkdir(parents=True, exist_ok=True)
    config.figures_dir.mkdir(parents=True, exist_ok=True)

    # Initialize components
    loader = HumanEvalLoader(use_evalplus=True)
    problems = loader.load_problems()

    generator = CodeLlamaGenerator(config)
    generator.load_model()

    mypy_verifier = MypyVerifier(timeout=config.mypy_timeout)
    pytest_verifier = PytestVerifier(timeout=config.pytest_timeout)
    classifier = DualSensitivityClassifier(k_samples=config.k_samples, variance_threshold=config.variance_threshold)

    # Process all tasks
    results = []
    qualified_tasks = []

    for idx, (task_id, problem) in enumerate(problems.items()):
        logger.info(f"Processing task {idx+1}/{len(problems)}: {task_id}")

        # Generate K=20 samples
        prompt = problem['prompt']
        samples = generator.generate_samples(prompt, k=config.k_samples)
        logger.info(f"  Generated {len(samples)} samples")

        # Verify with mypy
        mypy_results = mypy_verifier.verify_batch(samples)
        logger.info(f"  Mypy: {sum(mypy_results)}/{len(mypy_results)} passed")

        # Verify with pytest
        test_code = create_test_code(problem)
        pytest_results = pytest_verifier.verify_batch(samples, [test_code] * len(samples))
        logger.info(f"  Pytest: {sum(pytest_results)}/{len(pytest_results)} passed")

        # Classify
        result = classifier.classify_task(task_id, mypy_results, pytest_results)
        results.append(result)

        if result['qualified']:
            qualified_tasks.append(task_id)
            logger.info(f"  ✓ QUALIFIED (variance={result['variance']:.3f})")
        elif result['dual_sensitive']:
            logger.info(f"  - Dual-sensitive but high variance ({result['variance']:.3f})")
        else:
            logger.info(f"  - Not dual-sensitive")

        # Save intermediate checkpoint
        if (idx + 1) % 10 == 0:
            checkpoint = {
                'processed': idx + 1,
                'total': len(problems),
                'qualified_count': len(qualified_tasks),
                'results': results
            }
            with open(config.output_dir / 'checkpoint.json', 'w') as f:
                json.dump(checkpoint, f, indent=2)

    # Final results
    N = len(qualified_tasks)
    logger.info("=" * 80)
    logger.info(f"EXPERIMENT COMPLETE")
    logger.info(f"Qualified tasks: N = {N}")
    logger.info(f"Target: N ≥ {config.target_n}")
    logger.info(f"Gate: {'PASS' if N >= config.target_n else 'FAIL'}")
    logger.info("=" * 80)

    # Save results
    final_results = {
        'config': asdict(config),
        'summary': {
            'total_tasks': len(problems),
            'qualified_tasks': N,
            'target_n': config.target_n,
            'gate_result': 'PASS' if N >= config.target_n else 'FAIL'
        },
        'qualified_task_ids': qualified_tasks,
        'all_results': results
    }

    with open(config.output_dir / 'results.json', 'w') as f:
        json.dump(final_results, f, indent=2)

    # Generate visualizations
    generate_figures(results, config)

    return final_results

def generate_figures(results: List[Dict], config: ExperimentConfig):
    """Generate required figures"""
    logger.info("Generating figures...")

    # Extract data
    qualified = [r for r in results if r['qualified']]
    dual_sensitive = [r for r in results if r['dual_sensitive']]
    variances = [r['variance'] for r in results]

    # Figure 1: Gate metrics
    fig, ax = plt.subplots(figsize=(8, 6))
    metrics = ['Target N', 'Actual N']
    values = [config.target_n, len(qualified)]
    colors = ['red', 'green' if len(qualified) >= config.target_n else 'orange']
    ax.bar(metrics, values, color=colors, alpha=0.7)
    ax.axhline(y=config.target_n, color='red', linestyle='--', label=f'Threshold (N={config.target_n})')
    ax.set_ylabel('Number of Tasks')
    ax.set_title('H-E1 Gate Metrics: Target vs Actual')
    ax.legend()
    plt.tight_layout()
    plt.savefig(config.figures_dir / 'gate_metrics.png', dpi=300)
    plt.close()

    # Figure 2: Classification distribution
    fig, ax = plt.subplots(figsize=(8, 6))
    categories = ['Not Dual-Sensitive', 'Dual-Sensitive\n(High Variance)', 'Qualified\n(Low Variance)']
    counts = [
        len(results) - len(dual_sensitive),
        len(dual_sensitive) - len(qualified),
        len(qualified)
    ]
    colors = ['gray', 'orange', 'green']
    ax.bar(categories, counts, color=colors, alpha=0.7)
    ax.set_ylabel('Number of Tasks')
    ax.set_title('Task Classification Distribution')
    plt.tight_layout()
    plt.savefig(config.figures_dir / 'classification_distribution.png', dpi=300)
    plt.close()

    # Figure 3: Variance histogram
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(variances, bins=20, color='blue', alpha=0.7, edgecolor='black')
    ax.axvline(x=config.variance_threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold (SD={config.variance_threshold})')
    ax.set_xlabel('Within-Task Variance (SD)')
    ax.set_ylabel('Number of Tasks')
    ax.set_title('Variance Distribution Across Tasks')
    ax.legend()
    plt.tight_layout()
    plt.savefig(config.figures_dir / 'variance_histogram.png', dpi=300)
    plt.close()

    # Figure 4: Pattern scatter
    mypy_fail_counts = [r['mypy_fail_pytest_pass'] for r in results]
    pytest_fail_counts = [r['mypy_pass_pytest_fail'] for r in results]
    qualified_mask = [r['qualified'] for r in results]

    fig, ax = plt.subplots(figsize=(8, 8))
    for i, (x, y, q) in enumerate(zip(mypy_fail_counts, pytest_fail_counts, qualified_mask)):
        color = 'green' if q else 'gray'
        alpha = 0.8 if q else 0.3
        ax.scatter(x, y, color=color, alpha=alpha, s=50)

    ax.axhline(y=1, color='red', linestyle='--', alpha=0.5)
    ax.axvline(x=1, color='red', linestyle='--', alpha=0.5)
    ax.set_xlabel('Mypy Fail + Pytest Pass Count')
    ax.set_ylabel('Mypy Pass + Pytest Fail Count')
    ax.set_title('Dual-Sensitivity Pattern Distribution')
    ax.grid(True, alpha=0.3)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', alpha=0.8, label='Qualified'),
        Patch(facecolor='gray', alpha=0.3, label='Not Qualified')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig(config.figures_dir / 'pattern_scatter.png', dpi=300)
    plt.close()

    logger.info("Figures saved")

if __name__ == '__main__':
    config = ExperimentConfig()
    results = run_experiment(config)

    # Print final summary
    print("\n" + "=" * 80)
    print("H-E1 EXPERIMENT SUMMARY")
    print("=" * 80)
    print(f"Total tasks processed: {results['summary']['total_tasks']}")
    print(f"Qualified tasks (N): {results['summary']['qualified_tasks']}")
    print(f"Target (N ≥ 20): {results['summary']['target_n']}")
    print(f"Gate result: {results['summary']['gate_result']}")
    print("=" * 80)
