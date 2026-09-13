"""Three-phase doctest scanner for H-C1."""

import ast
import base64
import doctest
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm

from token_estimator import estimate_tokens


def phase_a(source: str) -> bool:
    """Pattern check: True if '>>>' appears anywhere in source."""
    return ">>>" in source


def phase_b(source: str) -> dict:
    """Parse AST, extract doctest examples from all docstring-bearing nodes."""
    result = {"ast_positive": False, "n_examples": 0, "error": None}
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        result["error"] = f"SyntaxError: {e}"
        return result
    except Exception as e:
        result["error"] = f"ParseError: {e}"
        return result

    parser = doctest.DocTestParser()
    node_types = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)
    for node in ast.walk(tree):
        if not isinstance(node, node_types):
            continue
        docstring = ast.get_docstring(node)
        if not docstring:
            continue
        try:
            examples = parser.get_examples(docstring)
        except Exception:
            continue
        result["n_examples"] += len(examples)

    result["ast_positive"] = result["n_examples"] > 0
    return result


def _build_wrapper(source: str) -> str:
    """Build the -c string passed to subprocess.run, using base64 to avoid quoting issues."""
    encoded = base64.b64encode(source.encode("utf-8")).decode("ascii")
    return (
        "import base64, types, doctest, sys\n"
        f"src = base64.b64decode('{encoded}').decode('utf-8')\n"
        "mod = types.ModuleType('__scanned__')\n"
        "exec(compile(src, '__scanned__', 'exec'), mod.__dict__)\n"
        "results = doctest.testmod(mod, verbose=False)\n"
        "sys.exit(0 if results.failed == 0 else 1)\n"
    )


def _classify_error(returncode: int, stderr: bytes) -> str:
    """Classify failure from returncode and stderr text."""
    stderr_str = stderr.decode("utf-8", errors="replace")
    if "ImportError" in stderr_str or "ModuleNotFoundError" in stderr_str:
        return "import_error"
    if "AssertionError" in stderr_str or "Failed example" in stderr_str:
        return "assertion_error"
    if "DocTestFailure" in stderr_str or "UnexpectedException" in stderr_str:
        return "wrong_output"
    return "exception"


def phase_c_worker(source: str, timeout: int = 5) -> dict:
    """Run doctest suite in isolated subprocess. Module-level for ProcessPoolExecutor pickling."""
    wrapper = _build_wrapper(source)
    try:
        proc = subprocess.run(
            [sys.executable, "-c", wrapper],
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "error_type": "timeout"}
    except Exception as e:
        return {"passed": False, "error_type": f"exception: {e}"}

    if proc.returncode == 0:
        return {"passed": True, "error_type": None}
    return {"passed": False, "error_type": _classify_error(proc.returncode, proc.stderr)}


def run_all_phases(samples: list, n_workers: int = 4) -> list:
    """Run Phase A+B sequentially, then Phase C in parallel via ProcessPoolExecutor."""
    per_file = []
    ast_positive_indices = []

    # Phase A + B: single-threaded
    for i, sample in enumerate(tqdm(samples, desc="Phase A+B")):
        source = sample.get("content", "")
        rec = {
            "file_id": str(i),
            "content_len": len(source),
            "phase_a": False,
            "phase_b": False,
            "n_doctest_examples": 0,
            "phase_c": None,
            "error_type": None,
            "parse_error": None,
            "estimated_tokens": 0,
        }
        try:
            rec["phase_a"] = phase_a(source)
            if rec["phase_a"]:
                b = phase_b(source)
                rec["phase_b"] = b["ast_positive"]
                rec["n_doctest_examples"] = b["n_examples"]
                rec["parse_error"] = b["error"]
                if rec["phase_b"]:
                    ast_positive_indices.append(i)
        except UnicodeDecodeError as e:
            rec["parse_error"] = f"UnicodeDecodeError: {e}"
        per_file.append(rec)

    print(f"Phase A complete: {sum(r['phase_a'] for r in per_file)} / {len(per_file)} files contain doctest patterns ({sum(r['phase_a'] for r in per_file)/len(per_file):.1%})")
    print(f"Phase B complete: {len(ast_positive_indices)} files with parseable doctests")

    # Phase C: parallel
    ast_sources = [(i, samples[i]["content"]) for i in ast_positive_indices]
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = {executor.submit(phase_c_worker, src): idx for idx, src in ast_sources}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Phase C"):
            idx = futures[future]
            try:
                c = future.result(timeout=10)
            except TimeoutError:
                c = {"passed": False, "error_type": "timeout"}
            except Exception as e:
                c = {"passed": False, "error_type": f"exception: {e}"}
            per_file[idx]["phase_c"] = c["passed"]
            per_file[idx]["error_type"] = c["error_type"]
            if c["passed"]:
                per_file[idx]["estimated_tokens"] = estimate_tokens(samples[idx]["content"])

    n_exec = sum(1 for r in per_file if r["phase_c"] is True)
    print(f"Phase C complete: {n_exec} / {len(per_file)} files have executable doctests ({n_exec/len(per_file):.1%})")

    return per_file
