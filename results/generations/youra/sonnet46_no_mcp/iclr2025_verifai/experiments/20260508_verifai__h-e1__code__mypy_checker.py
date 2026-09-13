import json
import os
import random
import re
import tempfile
from typing import Any, Dict, List, Tuple

import mypy.api


class MypyChecker:
    def check_code(self, code: str) -> Tuple[str, str, int]:
        """Write to temp file, run mypy.api.run(). Returns (stdout, stderr, exit_code)."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            stdout, stderr, exit_code = mypy.api.run(
                [tmp_path, "--ignore-missing-imports"]
            )
        finally:
            os.unlink(tmp_path)

        return stdout, stderr, exit_code

    def parse_output(self, stdout: str) -> List[dict]:
        """Parse mypy stdout into structured error list."""
        pattern = re.compile(
            r":(\d+):(\d+): \w+: (.+?)(?:\s+\[(.+?)\])?$"
        )
        errors = []
        for line in stdout.splitlines():
            m = pattern.search(line)
            if m:
                errors.append({
                    "line": int(m.group(1)),
                    "col": int(m.group(2)),
                    "message": m.group(3).strip(),
                    "error_code": m.group(4) if m.group(4) else None,
                })
        return errors

    def check_pool(
        self,
        pool: Dict[str, List[str]],
        output_path: str,
        sample_size: int = 50,
    ) -> Dict[str, Any]:
        """Run mypy on first completion of sample_size problems."""
        task_ids = list(pool.keys())
        if len(task_ids) > sample_size:
            random.seed(42)
            task_ids = random.sample(task_ids, sample_size)

        results: Dict[str, Any] = {}
        structured_count = 0

        for task_id in task_ids:
            completions = pool.get(task_id, [])
            if not completions:
                continue
            code = completions[0]
            stdout, stderr, exit_code = self.check_code(code)
            # exit_code 2 = syntax error; completions are already-indented function bodies
            # Prepend a dummy def header so mypy can analyze them as valid Python
            if exit_code == 2 and "indent" in stdout.lower():
                wrapped = "def _stub(*args, **kwargs):\n" + code
                stdout, stderr, exit_code = self.check_code(wrapped)
            parsed = self.parse_output(stdout)
            results[task_id] = {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "parsed_errors": parsed,
            }
            # exit_code in {0, 1} = structured output (0=clean, 1=errors found)
            if exit_code in (0, 1):
                structured_count += 1

        rate = structured_count / len(results) if results else 0.0
        print(f"  mypy structured rate: {structured_count}/{len(results)} = {rate:.2%}")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        return results
