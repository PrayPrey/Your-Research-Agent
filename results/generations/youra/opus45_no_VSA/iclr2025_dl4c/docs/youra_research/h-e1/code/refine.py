"""Self-refinement inference for H-E1 experiment."""
import subprocess
import tempfile
import torch
from transformers import PreTrainedModel, PreTrainedTokenizerBase

from config import Config


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


def single_shot(model: PreTrainedModel, tokenizer: PreTrainedTokenizerBase, prompt: str, cfg: Config) -> str:
    """Greedy (temperature=0) generation."""
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
    # Remove prompt from output if present
    if code.startswith(prompt):
        code = code[len(prompt):].strip()
    return code


def self_refine(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    prompt: str,
    tests: list[str],
    cfg: Config,
) -> str:
    """Up to K refine iterations using execution feedback."""
    code = single_shot(model, tokenizer, prompt, cfg)

    for i in range(cfg.refine_k):
        pass_rate, err_msg = execute_and_get_feedback(code, tests)
        if pass_rate == 1.0:
            return code

        refine_prompt = (
            f"{prompt}\n"
            f"# Previous attempt:\n{code}\n"
            f"# Error:\n{err_msg}\n"
            f"# Fixed code:"
        )
        code = single_shot(model, tokenizer, refine_prompt, cfg)

    return code
