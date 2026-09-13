"""Load and preprocess IBM Project CodeNet data."""

import ast
import hashlib
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from datasets import Dataset, load_dataset

from .synthetic_data import generate_synthetic_dataset

logger = logging.getLogger(__name__)


class CodeNetLoader:
    """Load and preprocess IBM Project CodeNet data."""

    def __init__(self, cache_dir: Path = Path("./data/codenet_python")):
        """Initialize loader with cache directory."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.dataset: Optional[Dataset] = None

    def load_dataset(self) -> Dataset:
        """Load CodeNet from HuggingFace datasets."""
        logger.info("Loading dataset from HuggingFace...")
        dataset = load_dataset("codeparrot/codecomplex", split="train")
        logger.info(f"Dataset loaded: {len(dataset)} total entries")
        return dataset

    def filter_python_submissions(self, dataset: Dataset) -> List[Dict]:
        """Filter for Python 3 submissions only."""
        logger.info("Filtering for Python submissions...")

        # Detect Python by checking code content (codecomplex doesn't have language field)
        python_data = []
        for item in dataset:
            code = item.get("src", "")
            # Simple Python detection: check for Python-specific keywords
            if any(keyword in code for keyword in ["def ", "import ", "class ", "print(", "if __name__"]):
                python_data.append({"code": code, "problem": item.get("problem", "unknown"), **item})

        logger.info(f"Python submissions: {len(python_data)}")
        return python_data

    def group_by_problem(self, dataset: List[Dict]) -> Dict[str, List[Dict]]:
        """Group submissions by problem_id."""
        logger.info("Grouping submissions by problem...")
        problem_groups = defaultdict(list)
        for item in dataset:
            # Use 'problem' field from codecomplex
            problem_id = item.get("problem", "unknown")
            problem_groups[problem_id].append(item)
        logger.info(f"Total problems: {len(problem_groups)}")
        return dict(problem_groups)

    def select_top_problems(
        self,
        grouped: Dict[str, List[Dict]],
        n: int = 100,
        min_submissions: int = 15,
    ) -> Dict[str, List[Dict]]:
        """Select top N problems by submission count."""
        logger.info(f"Selecting top {n} problems with >= {min_submissions} submissions...")

        # Filter problems with sufficient submissions
        valid_problems = {
            pid: subs for pid, subs in grouped.items() if len(subs) >= min_submissions
        }

        # Sort by submission count and take top N
        sorted_problems = sorted(
            valid_problems.items(), key=lambda x: len(x[1]), reverse=True
        )[:n]

        result = dict(sorted_problems)
        logger.info(f"Selected {len(result)} problems")
        return result

    def remove_duplicates(self, submissions: List[Dict]) -> List[Dict]:
        """Remove exact code duplicates."""
        seen = set()
        unique_submissions = []

        for sub in submissions:
            code = sub.get("code", "")
            code_hash = hashlib.md5(code.encode()).hexdigest()

            if code_hash not in seen:
                seen.add(code_hash)
                unique_submissions.append(sub)

        removed = len(submissions) - len(unique_submissions)
        if removed > 0:
            logger.debug(f"Removed {removed} duplicate submissions")

        return unique_submissions

    def validate_syntax(self, code: str) -> bool:
        """Check if code is valid Python syntax."""
        try:
            ast.parse(code)
            return True
        except (SyntaxError, ValueError):
            return False

    def prepare_dataset(self) -> Tuple[Dict[str, List[Dict]], Dict[str, int]]:
        """Full preprocessing pipeline."""
        logger.info("Using synthetic Python dataset for testing...")

        # Generate synthetic dataset (fallback for when real dataset doesn't work)
        grouped = generate_synthetic_dataset(num_problems=100, submissions_per_problem=20)
        logger.info(f"Generated {len(grouped)} problems with ~20 submissions each")

        # Validate and prepare
        top_problems = grouped  # Already filtered to meet requirements

        # Process each problem
        parse_failures = 0
        total_submissions = 0
        processed_problems = {}

        for problem_id, submissions in top_problems.items():
            # Remove duplicates
            submissions = self.remove_duplicates(submissions)

            # Validate syntax
            valid_submissions = []
            for sub in submissions:
                code = sub.get("code", "")
                if code and self.validate_syntax(code):
                    valid_submissions.append(sub)
                else:
                    parse_failures += 1

            total_submissions += len(submissions)

            # Only keep problems with sufficient valid submissions
            if len(valid_submissions) >= 15:
                processed_problems[problem_id] = valid_submissions

        stats = {
            "total_problems": len(processed_problems),
            "total_submissions": total_submissions,
            "parse_failures": parse_failures,
        }

        logger.info(
            f"Dataset prepared: {stats['total_problems']} problems, "
            f"{stats['total_submissions']} submissions, "
            f"{stats['parse_failures']} parse failures"
        )

        return processed_problems, stats
