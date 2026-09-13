import subprocess
import tempfile
import json
import os


class AnalyzerError(Exception):
    pass


def _run_subprocess_json(cmd: list[str], timeout_s: int, results_key: str | None = None) -> list[dict]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
        if not proc.stdout.strip():
            return []
        data = json.loads(proc.stdout)
        if results_key:
            return data.get(results_key, [])
        return data if isinstance(data, list) else []
    except subprocess.TimeoutExpired:
        return []
    except json.JSONDecodeError:
        return []


class BanditAnalyzer:
    def run(self, code: str, timeout_s: int = 30) -> list[dict]:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        try:
            return _run_subprocess_json(
                ["bandit", "-f", "json", tmp_path],
                timeout_s,
                results_key="results"
            )
        finally:
            os.unlink(tmp_path)


class PylintAnalyzer:
    def run(self, code: str, timeout_s: int = 30) -> list[dict]:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        try:
            return _run_subprocess_json(
                ["pylint", "--output-format=json", "--disable=C,R", tmp_path],
                timeout_s,
                results_key=None
            )
        finally:
            os.unlink(tmp_path)
