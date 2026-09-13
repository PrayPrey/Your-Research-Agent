"""Error classification pipeline using ast + mypy + pytest."""

import ast
import subprocess
import tempfile
from pathlib import Path
from typing import Literal, Optional, Tuple
import os


ErrorMode = Literal["syntax", "type", "semantic", "pass", "uncategorized"]


class ErrorClassifier:
    """Classify code errors via sequential pipeline."""

    def __init__(self, mypy_strict: bool = True, timeout_sec: int = 10):
        self.mypy_strict = mypy_strict
        self.timeout_sec = timeout_sec

    def check_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """Check syntax with ast.parse(). Returns: (is_valid, error_msg)."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def check_types(self, code: str) -> Tuple[bool, Optional[str]]:
        """Check types with mypy --strict. Returns: (is_valid, error_msg)."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            cmd = ['mypy', '--strict', '--no-error-summary', temp_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )

            if result.returncode == 0:
                return True, None
            else:
                return False, result.stdout + result.stderr

        except subprocess.TimeoutExpired:
            return False, "Mypy timeout"
        except Exception as e:
            return False, f"Mypy error: {e}"
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass

    def check_execution(
        self,
        code: str,
        test_code: str,
        timeout_sec: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """Execute tests with pytest. Returns: (is_pass, error_msg)."""
        if timeout_sec is None:
            timeout_sec = self.timeout_sec

        # Combine code and test
        full_code = f"{code}\n\n{test_code}"

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as f:
            f.write(full_code)
            f.flush()
            temp_path = f.name

        try:
            cmd = ['pytest', temp_path, '-v', '--tb=short', f'--timeout={timeout_sec}']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec + 5
            )

            if result.returncode == 0:
                return True, None
            else:
                return False, result.stdout + result.stderr

        except subprocess.TimeoutExpired:
            return False, "Execution timeout"
        except Exception as e:
            return False, f"Execution error: {e}"
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass

    def classify(self, code: str, test_code: str) -> Tuple[ErrorMode, Optional[str]]:
        """
        Classify error mode via sequential pipeline.
        Returns: (error_mode, error_detail)
        """
        try:
            # Step 1: Syntax check
            syntax_ok, syntax_err = self.check_syntax(code)
            if not syntax_ok:
                return "syntax", syntax_err

            # Step 2: Type check
            type_ok, type_err = self.check_types(code)
            if not type_ok:
                return "type", type_err

            # Step 3: Execution check
            exec_ok, exec_err = self.check_execution(code, test_code)
            if not exec_ok:
                return "semantic", exec_err

            # Step 4: All pass
            return "pass", None

        except Exception as e:
            return "uncategorized", str(e)
