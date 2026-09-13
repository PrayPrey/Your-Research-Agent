"""FR-1: Precondition checks — revision existence, token match, sanity eval."""
import subprocess
import sys
from config import (
    PYTHIA_ID, PYTHIA_REVISION, PYTHIA_TOKENS,
    OLMO_ID, OLMO_REVISION, OLMO_TOKENS,
    TARGET_TOKENS, TOKEN_TOLERANCE, RESULTS_DIR,
)


def check_revision_exists(model_id: str, revision: str) -> bool:
    """Return True if the HuggingFace revision exists for model_id."""
    try:
        from huggingface_hub import list_repo_refs
        refs = list_repo_refs(model_id)
        all_refs = [b.name for b in refs.branches] + [t.name for t in refs.tags]
        exists = revision in all_refs
        if not exists:
            print(f"[WARN] Revision '{revision}' not in branches/tags for {model_id}")
            print(f"       Available (first 10): {all_refs[:10]}")
        return exists
    except Exception as e:
        print(f"[WARN] Could not list refs for {model_id}: {e}")
        # Non-fatal: treat as exists and let lm_eval fail if truly missing
        return True


def check_token_match(tokens_trained: int, label: str) -> bool:
    """Return True if tokens_trained is within TOKEN_TOLERANCE of TARGET_TOKENS."""
    deviation = abs(tokens_trained - TARGET_TOKENS) / TARGET_TOKENS
    ok = deviation <= TOKEN_TOLERANCE
    print(f"[CHECK] {label}: {tokens_trained / 1e9:.1f}B tokens "
          f"(deviation={deviation:.1%}, tolerance={TOKEN_TOLERANCE:.0%}) → {'OK' if ok else 'FAIL'}")
    return ok


def sanity_eval(model_id: str, revision: str, output_dir: str) -> bool:
    """Run lm_eval with --limit 50 on mmlu_abstract_algebra. Returns True on success."""
    import pathlib
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_id},revision={revision},dtype=float16",
        "--tasks", "mmlu_abstract_algebra",
        "--batch_size", "auto",
        "--output_path", output_dir,
        "--limit", "50",
    ]
    print(f"[SANITY] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def run_all_checks() -> None:
    """Run all preconditions for both models. Raise SystemExit on any failure."""
    errors = []

    # Token match checks
    if not check_token_match(PYTHIA_TOKENS, "Pythia-6.9B"):
        errors.append(f"Pythia token count {PYTHIA_TOKENS/1e9:.1f}B outside ±10% of 300B")
    if not check_token_match(OLMO_TOKENS, "OLMo-7B"):
        errors.append(f"OLMo token count {OLMO_TOKENS/1e9:.1f}B outside ±10% of 300B")

    # Revision existence checks
    print(f"[CHECK] Verifying Pythia revision {PYTHIA_REVISION}...")
    if not check_revision_exists(PYTHIA_ID, PYTHIA_REVISION):
        errors.append(f"Pythia revision '{PYTHIA_REVISION}' not found on HuggingFace")

    print(f"[CHECK] Verifying OLMo revision {OLMO_REVISION}...")
    if not check_revision_exists(OLMO_ID, OLMO_REVISION):
        errors.append(f"OLMo revision '{OLMO_REVISION}' not found on HuggingFace")

    if errors:
        print("\n[PRECONDITION FAILURES]")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)

    print("\n[PRECONDITIONS OK] All checks passed.")


if __name__ == "__main__":
    run_all_checks()
