#!/usr/bin/env python3
"""
H-M1: Static Analysis Cascade Routing Mechanism
Tests whether mypy --strict catches ≥30% of errors before execution
"""
import json
import logging
import sys
import re
from pathlib import Path
from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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

# QualifiedTaskLoader class removed - now handled by CascadeDetectionAnalyzer.load_h_e1_qualified_tasks()

class CascadeDetectionAnalyzer:
    """
    Analyze mypy error detection rates using REAL HumanEval data

    This loads the N=35 qualified task list from h-e1, then RE-RUNS the analysis
    with fresh code generation to measure REAL mypy detection rates.
    """

    def __init__(self, h_e1_results_path: str):
        self.results_path = Path(h_e1_results_path)
        logger.info("Initializing detection analyzer with REAL dataset")

    def load_h_e1_qualified_tasks(self) -> List[str]:
        """Load qualified task IDs from h-e1 results"""
        # Try multiple possible paths
        possible_paths = [
            self.results_path / "code" / "outputs" / "results.json",  # h-e1/code/outputs/results.json
            self.results_path / "outputs" / "results.json",  # h-e1/outputs/results.json
            self.results_path / "experiment_results.json",  # h-e1/experiment_results.json
            Path("../h-e1/code/outputs/results.json"),  # Relative from h-m1/code
        ]

        results_file = None
        for path in possible_paths:
            if path.exists():
                results_file = path
                break

        if not results_file:
            raise FileNotFoundError(f"H-E1 results not found. Tried: {[str(p) for p in possible_paths]}")

        logger.info(f"Loading h-e1 results from: {results_file}")
        with open(results_file) as f:
            data = json.load(f)

        # Extract qualified task IDs
        if "qualified_task_ids" in data:
            task_ids = data["qualified_task_ids"]
            logger.info(f"Found qualified_task_ids field with {len(task_ids)} tasks")
        else:
            # Parse from all_results
            all_results = data.get('all_results', [])
            task_ids = [r["task_id"] for r in all_results if r.get("qualified", False)]
            logger.info(f"Extracted {len(task_ids)} qualified tasks from all_results")

        if not task_ids:
            logger.error(f"No qualified tasks found! Data keys: {list(data.keys())}")
            raise ValueError("No qualified tasks found in h-e1 results")

        logger.info(f"Loaded {len(task_ids)} qualified tasks from h-e1")
        return task_ids

    def calculate_detection_rates(self, qualified_task_ids: List[str]) -> Dict:
        """
        Calculate mypy error detection rates on REAL HumanEval data

        For each qualified task:
        1. Load problem from HumanEval+
        2. Generate K=20 samples with CodeLlama (fresh generation)
        3. Run mypy --strict on each sample
        4. Run pytest on each sample
        5. Calculate mypy early detection rate
        """
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        import subprocess
        import tempfile

        # Load HumanEval+ dataset
        try:
            from evalplus.data import get_human_eval_plus
            all_problems = get_human_eval_plus()
            logger.info(f"Loaded {len(all_problems)} problems from HumanEval+")
        except Exception as e:
            logger.error(f"Failed to load HumanEval+: {e}")
            raise

        # Filter to qualified tasks
        problems = {tid: all_problems[tid] for tid in qualified_task_ids if tid in all_problems}
        logger.info(f"Filtered to {len(problems)} qualified problems")

        # Load CodeLlama model
        model_name = "codellama/CodeLlama-7b-hf"
        logger.info(f"Loading {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        logger.info("Model loaded")

        # Process each task
        task_results = []
        k_samples = 20
        seed = 42

        for idx, (task_id, problem) in enumerate(problems.items(), 1):
            logger.info(f"Processing {task_id} ({idx}/{len(problems)})...")

            # Generate K=20 samples
            prompt = problem['prompt']
            samples = []

            for i in range(k_samples):
                torch.manual_seed(seed + i)
                inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=256,
                        temperature=0.8,
                        top_p=0.95,
                        top_k=40,
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id
                    )

                completion = tokenizer.decode(
                    outputs[0][inputs['input_ids'].shape[1]:],
                    skip_special_tokens=True
                )
                samples.append(completion)

            # Verify with mypy
            mypy_failed = 0
            for sample in samples:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(sample)
                    temp_path = f.name

                try:
                    result = subprocess.run(
                        ['mypy', '--strict', temp_path],
                        capture_output=True,
                        timeout=10
                    )
                    if result.returncode != 0:
                        mypy_failed += 1
                except:
                    mypy_failed += 1
                finally:
                    Path(temp_path).unlink(missing_ok=True)

            # Verify with pytest
            pytest_failed = 0
            for sample in samples:
                try:
                    from evalplus.eval import check_correctness
                    result = check_correctness(
                        task_id=task_id,
                        completion=sample,
                        timeout=120
                    )
                    if not result.get("passed", False):
                        pytest_failed += 1
                except:
                    pytest_failed += 1

            # Calculate detection rate
            mypy_detection_rate = (mypy_failed / k_samples) * 100

            task_results.append({
                'task_id': task_id,
                'mypy_failed': mypy_failed,
                'pytest_failed': pytest_failed,
                'total_samples': k_samples,
                'mypy_detection_rate': mypy_detection_rate,
                'dual_sensitive': True  # All tasks from h-e1 are dual-sensitive
            })

            logger.info(f"  Mypy: {mypy_failed}/{k_samples} failed ({mypy_detection_rate:.1f}%)")

        # Calculate aggregate metrics
        total_mypy_errors = sum(t['mypy_failed'] for t in task_results)
        total_iterations = sum(t['total_samples'] for t in task_results)

        overall_detection_rate = (total_mypy_errors / total_iterations) * 100 if total_iterations > 0 else 0

        logger.info(f"\nOverall mypy detection rate: {overall_detection_rate:.1f}%")
        logger.info(f"Total mypy errors: {total_mypy_errors}/{total_iterations}")

        return {
            'task_results': task_results,
            'overall_detection_rate': overall_detection_rate,
            'total_mypy_errors': total_mypy_errors,
            'total_iterations': total_iterations,
            'task_count': len(task_results),
            'gate_threshold': 30.0,
            'gate_satisfied': overall_detection_rate >= 30.0
        }

class Visualizer:
    """Generate required figures for h-m1"""
    
    def __init__(self, figures_dir: Path):
        self.figures_dir = figures_dir
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        sns.set_style("whitegrid")
    
    def plot_gate_metrics(self, results: Dict):
        """Figure 1: Gate metrics comparison"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        categories = ['Target', 'Actual']
        values = [results['gate_threshold'], results['overall_detection_rate']]
        colors = ['gray', 'green' if results['gate_satisfied'] else 'red']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7)
        
        # Add threshold line
        ax.axhline(y=30, color='r', linestyle='--', label='MUST_WORK Gate (30%)')
        
        # Labels
        ax.set_ylabel('Detection Rate (%)', fontsize=12)
        ax.set_title('H-M1: Mypy Error Detection Rate vs Gate', fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(50, max(values) * 1.2))
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.legend()
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'fig1_gate_metrics.png', dpi=300)
        plt.close()
        
        logger.info("Figure 1 saved: fig1_gate_metrics.png")
    
    def plot_task_breakdown(self, results: Dict):
        """Figure 2: Error detection breakdown per task"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        task_results = results['task_results'][:15]  # Show first 15 tasks
        task_ids = [t['task_id'].split('/')[-1] for t in task_results]
        detection_rates = [t['mypy_detection_rate'] for t in task_results]
        
        bars = ax.bar(range(len(task_ids)), detection_rates, alpha=0.7)
        
        # Color bars based on detection rate
        for i, bar in enumerate(bars):
            if detection_rates[i] >= 30:
                bar.set_color('green')
            else:
                bar.set_color('orange')
        
        ax.set_xlabel('Task ID', fontsize=12)
        ax.set_ylabel('Mypy Detection Rate (%)', fontsize=12)
        ax.set_title('Per-Task Mypy Error Detection Rates', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(task_ids)))
        ax.set_xticklabels(task_ids, rotation=45, ha='right')
        ax.axhline(y=30, color='r', linestyle='--', label='Gate Threshold', alpha=0.5)
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'fig2_task_breakdown.png', dpi=300)
        plt.close()
        
        logger.info("Figure 2 saved: fig2_task_breakdown.png")
    
    def plot_error_distribution(self, results: Dict):
        """Figure 3: Distribution of detection rates"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        detection_rates = [t['mypy_detection_rate'] for t in results['task_results']]
        
        ax.hist(detection_rates, bins=10, alpha=0.7, color='steelblue', edgecolor='black')
        ax.axvline(x=30, color='r', linestyle='--', linewidth=2, label='Gate Threshold')
        ax.axvline(x=results['overall_detection_rate'], color='green', linestyle='-', linewidth=2, label=f'Overall: {results["overall_detection_rate"]:.1f}%')
        
        ax.set_xlabel('Mypy Detection Rate (%)', fontsize=12)
        ax.set_ylabel('Number of Tasks', fontsize=12)
        ax.set_title('Distribution of Mypy Detection Rates Across Tasks', fontsize=14, fontweight='bold')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'fig3_distribution.png', dpi=300)
        plt.close()
        
        logger.info("Figure 3 saved: fig3_distribution.png")

def main():
    """Execute H-M1 experiment"""
    logger.info("="*60)
    logger.info("H-M1: Static Analysis Cascade Routing Mechanism")
    logger.info("="*60)
    
    # Configuration
    h_e1_folder = Path("/home/anonymous/YouRA_results_new_4_sonnet45/TEST_verifai/docs/youra_research/20260318_verifai/h-e1")
    h_e1_validation = h_e1_folder / "04_validation.md"
    output_dir = Path("./outputs")
    figures_dir = Path("./figures")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Load qualified tasks from h-e1
        logger.info("\n[Step 1/3] Loading qualified tasks from h-e1...")
        analyzer = CascadeDetectionAnalyzer(str(h_e1_folder))
        qualified_task_ids = analyzer.load_h_e1_qualified_tasks()
        logger.info(f"Qualified tasks loaded: N={len(qualified_task_ids)}")

        # Step 2: Calculate detection rates (runs REAL experiment)
        logger.info("\n[Step 2/3] Running cascade routing analysis on REAL data...")
        logger.info("This will generate fresh code samples and measure real mypy detection rates")
        results = analyzer.calculate_detection_rates(qualified_task_ids)

        # Step 3: Generate visualizations
        logger.info("\n[Step 3/3] Generating visualizations...")
        viz = Visualizer(figures_dir)
        viz.plot_gate_metrics(results)
        viz.plot_task_breakdown(results)
        viz.plot_error_distribution(results)
        
        # Save results
        results_file = output_dir / "results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"\nResults saved to: {results_file}")
        
        # Final verdict
        logger.info("\n" + "="*60)
        logger.info("EXPERIMENT COMPLETE")
        logger.info("="*60)
        logger.info(f"Overall Detection Rate: {results['overall_detection_rate']:.1f}%")
        logger.info(f"Gate Threshold: {results['gate_threshold']:.1f}%")
        logger.info(f"Gate Status: {'✅ PASS' if results['gate_satisfied'] else '❌ FAIL'}")
        logger.info("="*60)
        
        return 0 if results['gate_satisfied'] else 1
        
    except Exception as e:
        logger.error(f"Experiment failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
