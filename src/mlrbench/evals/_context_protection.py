"""Shared context-overflow protection for evaluator dispatchers.

Centralises the cap-ladder, combined-truncation, and multi-provider
context-length detection used across overall_review and eval_hallucination
for all systems (youra, ai_scientist_v2, mlragent). Patterns mirror the
operational `_with_code.py` runners.
"""
from __future__ import annotations


CODE_TOTAL_CAP_LADDER = [None, 600_000, 300_000, 150_000, 60_000]


def is_context_length_error(error):
    """Return True if `error` means the prompt was too big for the model.

    Covers OpenAI ("maximum context length", "reduce the length"),
    xAI/grok ("maximum prompt length"), Google/gemini ("maximum number of
    tokens", "input token count exceeds"), Anthropic ("prompt is too
    long"), and the generic "context window" / "input exceeds" phrasings
    seen via the OpenRouter proxy.
    """
    text = str(error).lower()
    return any(
        p in text
        for p in (
            "maximum context length",
            "context length",
            "context window",
            "exceeds the context window",
            "input exceeds",
            "reduce the length",
            "too many tokens",
            "maximum prompt length",
            "input size exceeds",
            "maximum number of tokens",
            "input token count exceeds",
            "prompt is too long",
            "completion_tokens",
            "prompt_tokens",
            "total_tokens",
        )
    )


def truncate_combined(code_content, max_code_total_chars):
    """Apply a combined character cap to an assembled code-context string."""
    if (
        max_code_total_chars is not None
        and len(code_content) > max_code_total_chars
    ):
        code_content = (
            code_content[:max_code_total_chars]
            + "\n\n[Stopped: combined code context truncated to "
            + f"{max_code_total_chars} characters by overall_review]\n"
        )
    return code_content


def review_with_code_cap_ladder(attempt_fn, *, ladder=None):
    """Run `attempt_fn(cap)` along a code-context cap ladder.

    `attempt_fn(cap)` must:
      * return a non-None result on success;
      * raise an exception that satisfies `is_context_length_error(...)` to
        trigger retry at the next smaller cap;
      * raise any other exception to abort the ladder (returns None);
      * return None to signal a non-retryable internal failure (returns
        None).
    Returns None if every ladder rung still overflowed.
    """
    if ladder is None:
        ladder = CODE_TOTAL_CAP_LADDER
    for cap in ladder:
        cap_label = "none (full)" if cap is None else f"{cap} chars"
        try:
            result = attempt_fn(cap)
            if result is not None:
                if cap is not None:
                    print(f"  [OK] Succeeded with code total cap {cap} chars.")
                return result
            print(
                "  [FAIL] attempt returned no result (not a context error);"
                " not retrying smaller."
            )
            return None
        except Exception as exc:
            print(f"Attempt (code cap: {cap_label}) failed: {str(exc)}")
            if not is_context_length_error(exc):
                print("  [FAIL] Non-context error; not retrying smaller.")
                return None
            print("  Context too long; retrying with a smaller code cap...")
    print(
        "  [SKIP] Context still too long at the smallest code cap "
        f"({ladder[-1]} chars); skipping evaluation."
    )
    return None
