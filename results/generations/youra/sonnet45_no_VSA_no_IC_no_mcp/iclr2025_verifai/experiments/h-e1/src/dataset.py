"""Dataset loader for code generation benchmarks."""

from datasets import load_dataset
from typing import Optional


class BenchmarkLoader:
    """Load standard code generation benchmarks."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir

    def load_humaneval(self, limit: int = 50) -> list[dict]:
        """Load HumanEval test split."""
        dataset = load_dataset("openai_humaneval", split="test", cache_dir=self.cache_dir)
        dataset = dataset.select(range(min(limit, len(dataset))))
        return [
            {
                "id": item["task_id"],
                "prompt": item["prompt"],
                "test": item["test"],
                "entry_point": item["entry_point"]
            }
            for item in dataset
        ]

    def load_mbpp(self, limit: int = 50) -> list[dict]:
        """Load MBPP test split."""
        dataset = load_dataset("mbpp", "sanitized", split="test", cache_dir=self.cache_dir)
        dataset = dataset.select(range(min(limit, len(dataset))))
        return [
            {
                "id": f"MBPP/{item['task_id']}",
                "prompt": item["prompt"] + "\n" + item["code"],
                "test": "\n".join(item["test_list"]),
                "entry_point": None
            }
            for item in dataset
        ]

    def load_codecontests(self, limit: int = 50) -> list[dict]:
        """Load CodeContests test split."""
        dataset = load_dataset("deepmind/code_contests", split="test", cache_dir=self.cache_dir)
        dataset = dataset.select(range(min(limit, len(dataset))))

        results = []
        for idx, item in enumerate(dataset):
            # CodeContests structure: description + tests
            prompt = item["description"]
            # Use Python3 tests if available
            tests = item.get("public_tests", {})
            test_cases = []
            if "input" in tests and "output" in tests:
                for inp, out in zip(tests["input"], tests["output"]):
                    test_cases.append(f"assert solution({repr(inp)}) == {repr(out)}")

            results.append({
                "id": f"CodeContests/{item.get('name', idx)}",
                "prompt": prompt,
                "test": "\n".join(test_cases) if test_cases else "pass",
                "entry_point": "solution"
            })

        return results

    def load_humaneval_x(self) -> list[dict]:
        """Load HumanEval-X Python split (164 problems)."""
        dataset = load_dataset("THUDM/humaneval-x", "python", split="test", cache_dir=self.cache_dir)
        return [
            {
                "id": item["task_id"],
                "prompt": item["prompt"],
                "test": item["test"],
                "entry_point": item.get("entry_point", None)
            }
            for item in dataset
        ]

    def load_all(self) -> dict[str, list[dict]]:
        """Load all benchmarks. Returns: {benchmark_name: [problems]}"""
        print("Loading HumanEval...")
        humaneval = self.load_humaneval()
        print(f"  Loaded {len(humaneval)} problems")

        print("Loading MBPP...")
        mbpp = self.load_mbpp()
        print(f"  Loaded {len(mbpp)} problems")

        print("Loading CodeContests...")
        codecontests = self.load_codecontests()
        print(f"  Loaded {len(codecontests)} problems")

        # HumanEval-X skipped (deprecated dataset script)
        print("HumanEval-X: Skipped (deprecated dataset format)")

        total = len(humaneval) + len(mbpp) + len(codecontests)
        print(f"\nTotal: {total} problems")

        return {
            "humaneval": humaneval,
            "mbpp": mbpp,
            "codecontests": codecontests
        }
