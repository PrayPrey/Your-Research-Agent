import json
from pathlib import Path

ARCHIVE = "docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results"
HE_FILE = "humaneval_samples_eval_results.json"
MBPP_FILE = "mbpp_samples_eval_results.json"
HE_EXPECTED = 34
MBPP_EXPECTED = 100
TOTAL_EXPECTED = 134


def load_failures(archive: str = ARCHIVE) -> tuple[dict, dict]:
    he_path = Path(archive) / HE_FILE
    mbpp_path = Path(archive) / MBPP_FILE

    if not he_path.exists():
        raise FileNotFoundError(f"HE+ results not found: {he_path}")
    if not mbpp_path.exists():
        raise FileNotFoundError(f"MBPP+ results not found: {mbpp_path}")

    with open(he_path) as f:
        he_raw = json.load(f)["eval"]
    with open(mbpp_path) as f:
        mbpp_raw = json.load(f)["eval"]

    he_failures = {tid: recs[0] for tid, recs in he_raw.items()
                   if recs and recs[0]["plus_status"] == "fail"}
    mbpp_failures = {tid: recs[0] for tid, recs in mbpp_raw.items()
                     if recs and recs[0]["plus_status"] == "fail"}

    return he_failures, mbpp_failures


def verify_counts(he_failures: dict, mbpp_failures: dict) -> None:
    assert len(he_failures) == HE_EXPECTED, \
        f"Expected {HE_EXPECTED} HE+ failures, got {len(he_failures)}"
    assert len(mbpp_failures) == MBPP_EXPECTED, \
        f"Expected {MBPP_EXPECTED} MBPP+ failures, got {len(mbpp_failures)}"
    assert len(he_failures) + len(mbpp_failures) == TOTAL_EXPECTED


def verify_fields(failures: dict) -> None:
    for tid, rec in failures.items():
        assert rec.get("solution"), f"Empty/missing solution for {tid}"
        assert rec.get("plus_fail_tests"), f"Empty/missing plus_fail_tests for {tid}"
