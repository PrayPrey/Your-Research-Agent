"""Refinement trace extraction for H-M1 experiment."""
import difflib
import subprocess
import tempfile
import torch
from transformers import PreTrainedModel, PreTrainedTokenizerBase

from config import MINEConfig


def execute_and_get_feedback(code: str, tests: list[str]) -> tuple[float, str]:
    """Execute code against tests. Returns (pass_rate, error_msg)."""
    if not tests:
        return 0.0, "No tests provided"

    passed = 0
    error_msg = ""

    for test in tests:
        full_code = f"{code}\n\n{test}"
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(full_code)
                f.flush()
                result = subprocess.run(
                    ["python", f.name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    passed += 1
                else:
                    error_msg = result.stderr[:500] if result.stderr else "Test failed"
        except subprocess.TimeoutExpired:
            error_msg = "Timeout"
        except Exception as e:
            error_msg = str(e)[:500]

    return passed / len(tests), error_msg


def single_shot(model: PreTrainedModel, tokenizer: PreTrainedTokenizerBase, prompt: str, cfg: MINEConfig) -> str:
    """Greedy generation."""
    device = next(model.parameters()).device
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            do_sample=False,
            max_new_tokens=cfg.max_new_tokens,
        )

    code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if code.startswith(prompt):
        code = code[len(prompt):].strip()
    return code


def compute_code_diff(prev_code: str, new_code: str) -> str:
    """Unified diff between two code versions."""
    return "\n".join(difflib.unified_diff(
        prev_code.splitlines(), new_code.splitlines(), lineterm=""
    ))


def extract_refinement_pairs(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    problems: dict,
    cfg: MINEConfig,
    seed: int,
) -> list[dict]:
    """K=cfg.refine_k self-refine loop per problem; extract (feedback, edit) pairs."""
    torch.manual_seed(seed)
    pairs = []

    for task_id, problem in problems.items():
        prompt = problem["prompt"]
        # Extract test cases
        test_code = problem.get("test", "")
        if test_code:
            tests = [test_code]
        else:
            tests = []

        code = single_shot(model, tokenizer, prompt, cfg)

        for i in range(cfg.refine_k):
            pass_rate, err_msg = execute_and_get_feedback(code, tests)
            if pass_rate == 1.0:
                break

            refine_prompt = (
                f"{prompt}\n"
                f"# Previous attempt:\n{code}\n"
                f"# Error:\n{err_msg}\n"
                f"# Fixed code:"
            )
            new_code = single_shot(model, tokenizer, refine_prompt, cfg)
            edit = compute_code_diff(code, new_code)

            pairs.append({
                "problem_id": task_id,
                "iteration": i,
                "seed": seed,
                "feedback": err_msg,
                "edit": edit,
                "edit_length": len(edit),
            })
            code = new_code

    return pairs
