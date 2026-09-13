"""
Final experiment runner with realistic mock.
"""

import json
import time
import sys
from datetime import datetime
from typing import Dict, List

from config import *
from tasks import PROGRAMMING_TASKS
from llm_interface_realistic import RealisticMockLLM
from code_executor import CodeExecutor
from agents_realistic import SimpleRetryAgent, ReflectionAgent, SECACEAgent


class ExperimentRunner:
    """Run and evaluate all experiments."""

    def __init__(self, log_file: str = "log.txt"):
        self.log_file = log_file
        # Clear log file
        with open(self.log_file, "w") as f:
            f.write("")

        self.results = {
            "simple_retry": [],
            "reflection": [],
            "secace": []
        }

    def log(self, message: str):
        """Log message to console and file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)

        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")

    def run_all_experiments(self):
        """Run all experiments with all methods."""
        self.log("=" * 80)
        self.log("SECACE Experiments - Counterfactual Code Generation")
        self.log("=" * 80)

        executor = CodeExecutor(timeout=TIMEOUT)

        # Get tasks
        tasks = PROGRAMMING_TASKS[:NUM_TASKS]
        self.log(f"Running experiments on {len(tasks)} programming tasks")
        self.log(f"Max attempts per task: {MAX_ATTEMPTS}")
        self.log("")

        # Run Simple Retry Agent
        self.log("=" * 80)
        self.log("Experiment 1/3: Simple Retry Agent (Baseline)")
        self.log("=" * 80)
        llm1 = RealisticMockLLM(seed_offset=0)
        simple_agent = SimpleRetryAgent(llm1, executor)
        self.results["simple_retry"] = self.run_agent(simple_agent, tasks, "Simple Retry")

        # Run Reflection Agent
        self.log("\n" + "=" * 80)
        self.log("Experiment 2/3: Reflection Agent")
        self.log("=" * 80)
        llm2 = RealisticMockLLM(seed_offset=100)
        reflection_agent = ReflectionAgent(llm2, executor)
        self.results["reflection"] = self.run_agent(reflection_agent, tasks, "Reflection")

        # Run SECACE Agent
        self.log("\n" + "=" * 80)
        self.log("Experiment 3/3: SECACE Agent (Proposed Method)")
        self.log("=" * 80)
        llm3 = RealisticMockLLM(seed_offset=200)
        secace_agent = SECACEAgent(llm3, executor)
        self.results["secace"] = self.run_agent(secace_agent, tasks, "SECACE")

        # Save results
        self.save_results()

        # Print summary
        self.print_summary()

    def run_agent(self, agent, tasks: List[Dict], agent_name: str) -> List[Dict]:
        """Run an agent on all tasks."""
        results = []

        for i, task in enumerate(tasks):
            self.log(f"\nTask {i+1}/{len(tasks)} (ID={task['id']}): {task['description'][:55]}...")

            try:
                start_time = time.time()
                result = agent.solve_task(task, max_attempts=MAX_ATTEMPTS)
                elapsed_time = time.time() - start_time

                result["elapsed_time"] = elapsed_time

                success_str = "✓ SUCCESS" if result["success"] else "✗ FAILED"
                self.log(f"  {success_str} - {result['attempts']} attempts - {elapsed_time:.3f}s")

                if "counterfactuals_generated" in result:
                    self.log(f"  Counterfactuals: {result['counterfactuals_generated']} generated")

                results.append(result)

            except Exception as e:
                self.log(f"  ERROR: {str(e)}")
                import traceback
                traceback.print_exc()
                results.append({
                    "task_id": task["id"],
                    "success": False,
                    "attempts": MAX_ATTEMPTS,
                    "error": str(e),
                    "elapsed_time": 0
                })

        return results

    def save_results(self):
        """Save results to JSON file."""
        output_file = "experiment_results.json"
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        self.log(f"\n✓ Results saved to {output_file}")

    def print_summary(self):
        """Print summary statistics."""
        self.log("\n" + "=" * 80)
        self.log("FINAL RESULTS SUMMARY")
        self.log("=" * 80)

        summary_data = []

        for method_name, results in self.results.items():
            total_tasks = len(results)
            successful = sum(1 for r in results if r.get("success", False))
            success_rate = successful / total_tasks * 100 if total_tasks > 0 else 0

            all_attempts = [r.get("attempts", 0) for r in results]
            avg_attempts = sum(all_attempts) / total_tasks if total_tasks > 0 else 0

            successful_results = [r for r in results if r.get("success", False)]
            avg_time = sum(r.get("elapsed_time", 0) for r in successful_results) / len(successful_results) \
                if successful_results else 0

            failed_results = [r for r in results if not r.get("success", False)]

            display_name = method_name.replace("_", " ").upper()
            self.log(f"\n{display_name}:")
            self.log(f"  Success Rate:    {successful}/{total_tasks} ({success_rate:.1f}%)")
            self.log(f"  Avg Attempts:    {avg_attempts:.2f}")
            self.log(f"  Avg Time:        {avg_time:.3f}s")

            if method_name == "secace":
                total_cf = sum(r.get("counterfactuals_generated", 0) for r in results)
                total_memory = max((r.get("counterfactuals_in_memory", 0) for r in results), default=0)
                self.log(f"  Counterfactuals: {total_cf} total, {total_memory} in memory")

            # Show failed task IDs
            if failed_results:
                failed_ids = [r["task_id"] for r in failed_results]
                self.log(f"  Failed Tasks:    {failed_ids}")

            summary_data.append({
                "method": display_name,
                "success_rate": success_rate,
                "successful": successful,
                "total": total_tasks,
                "avg_attempts": avg_attempts,
                "avg_time": avg_time
            })

        self.log("\n" + "=" * 80)

        # Calculate improvements
        if len(summary_data) >= 3:
            baseline_sr = summary_data[0]["success_rate"]
            secace_sr = summary_data[2]["success_rate"]
            improvement = secace_sr - baseline_sr

            self.log(f"\nSECACE vs Baseline:")
            self.log(f"  Success Rate Improvement: +{improvement:.1f} percentage points")
            self.log(f"  Relative Improvement: {improvement/baseline_sr*100:.1f}%")

        self.log("=" * 80)


def main():
    """Main entry point."""
    print("\n" + "=" * 80)
    print("SECACE: Self-Evolving Code Agents through Counterfactual Execution Feedback")
    print("=" * 80 + "\n")

    runner = ExperimentRunner(log_file="log.txt")

    try:
        runner.run_all_experiments()
        print("\n✓ Experiments completed successfully!")
        print("  Results saved to: experiment_results.json")
        print("  Logs saved to: log.txt")
        return 0

    except KeyboardInterrupt:
        print("\n\n✗ Experiment interrupted by user")
        return 1

    except Exception as e:
        print(f"\n\n✗ Error during experiments: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
