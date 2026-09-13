import json
import os
import subprocess
import tempfile

import config

def run_pylint_analysis(code: str) -> dict:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            ["pylint", tmp_path] + config.PYLINT_ARGS,
            capture_output=True,
            text=True,
            timeout=config.PYLINT_TIMEOUT_SEC,
        )

        try:
            messages = json.loads(result.stdout) if result.stdout.strip() else []
        except json.JSONDecodeError:
            messages = []

        actionable_count = sum(
            1 for m in messages if m.get("type") in config.ACTIONABLE_TYPES
        )

        return {
            "total_messages": len(messages),
            "actionable_count": actionable_count,
            "messages": messages,
        }

    except subprocess.TimeoutExpired:
        return {"total_messages": 0, "actionable_count": 0, "messages": []}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
