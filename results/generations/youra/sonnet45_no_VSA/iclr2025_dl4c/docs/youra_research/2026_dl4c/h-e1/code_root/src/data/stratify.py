"""Task stratification module for SWE-bench sampling."""
import json
import random
from collections import Counter, defaultdict
from typing import Dict, List
from datasets import load_dataset


class TaskStratifier:
    """Stratify SWE-bench tasks to match PurpleLlama CWE distribution."""

    def __init__(self, target_cwe_dist: Dict[str, float], cwe_keywords: Dict[str, List[str]], seed: int = 42):
        self.target_dist = target_cwe_dist
        self.cwe_keywords = cwe_keywords
        self.seed = seed
        random.seed(seed)

    def stratify_tasks(self, dataset, n_samples: int = 100, min_per_cwe: int = 5) -> List[Dict]:
        """Stratify SWE-bench tasks to match target CWE distribution."""
        # Predict CWE for each task
        tasks_by_cwe = defaultdict(list)
        for idx, task in enumerate(dataset):
            cwes = self._predict_cwe(task.get('problem_statement', ''))
            if cwes:
                primary_cwe = cwes[0]
                tasks_by_cwe[primary_cwe].append({
                    'task_id': task.get('instance_id', f'task_{idx}'),
                    'problem_statement': task.get('problem_statement', ''),
                    'repo': task.get('repo', ''),
                    'base_commit': task.get('base_commit', ''),
                    'predicted_cwe': primary_cwe
                })

        # Stratified sampling
        sampled_tasks = []
        remaining_samples = n_samples

        for cwe, proportion in self.target_dist.items():
            target_count = max(min_per_cwe, int(n_samples * proportion))
            available = tasks_by_cwe.get(cwe, [])

            if len(available) >= target_count:
                sampled = random.sample(available, target_count)
            else:
                sampled = available

            sampled_tasks.extend(sampled)
            remaining_samples -= len(sampled)

        # Fill remaining slots with any available tasks
        all_remaining = [t for cwe, tasks in tasks_by_cwe.items()
                        for t in tasks if t not in sampled_tasks]
        if remaining_samples > 0 and all_remaining:
            additional = random.sample(all_remaining, min(remaining_samples, len(all_remaining)))
            sampled_tasks.extend(additional)

        return sampled_tasks[:n_samples]

    def _predict_cwe(self, task_description: str) -> List[str]:
        """Predict CWE categories from task description using keyword matching."""
        task_lower = task_description.lower()
        matches = []

        for cwe, keywords in self.cwe_keywords.items():
            for keyword in keywords:
                if keyword in task_lower:
                    matches.append(cwe)
                    break

        return matches if matches else ['CWE-20']  # Default to input validation

    def get_stratification_report(self, tasks: List[Dict]) -> Dict:
        """Generate stratification statistics."""
        cwe_counts = Counter([t['predicted_cwe'] for t in tasks])
        return {
            'total_tasks': len(tasks),
            'cwe_distribution': dict(cwe_counts),
            'task_ids': [t['task_id'] for t in tasks]
        }
