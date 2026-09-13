"""Tests for analyze_reward_fractions.py — H-M2."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from analyze_reward_fractions import (
    load_reward_log,
    compute_nonzero_fractions,
    compute_step_series,
    save_results,
    assert_gate,
    detect_nonzero,
)


def _write_jsonl(path, records):
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


SAMPLE_RECORDS = [
    {"step": 1, "loss": 0.5, "intro_reward": 0.2, "interview_reward": 0.1, "competition_reward": 0.15},
    {"step": 2, "loss": 0.4, "intro_reward": 0.3, "interview_reward": 0.0, "competition_reward": 0.0},
    {"step": 3, "loss": 0.45, "intro_reward": 0.4, "interview_reward": 0.2, "competition_reward": 0.25},
    {"step": 4, "loss": 0.38, "intro_reward": None, "interview_reward": 0.15, "competition_reward": None},
    {"step": 5, "loss": 0.42, "intro_reward": 0.5, "interview_reward": 0.3, "competition_reward": 0.35},
]


def test_load_reward_log():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in SAMPLE_RECORDS:
            f.write(json.dumps(r) + "\n")
        f.write("malformed line\n")
        path = f.name
    records = load_reward_log(path)
    assert len(records) == len(SAMPLE_RECORDS), f"Expected {len(SAMPLE_RECORDS)}, got {len(records)}"


def test_compute_nonzero_fractions():
    fracs = compute_nonzero_fractions(SAMPLE_RECORDS)
    assert "introductory" in fracs
    assert "interview" in fracs
    assert "competition" in fracs
    # intro: steps 1,2,3,5 have reward (4 steps), nonzero = 0.2>0=T, 0.3>0=T, 0.4>0=T, 0.5>0=T -> 4/4=1.0
    assert fracs["introductory"] == 1.0, f"Expected 1.0, got {fracs['introductory']}"
    # competition: steps 1,3,5 have reward, 0.15>0=T, 0.0>0=F, 0.25>0=T, 0.35>0=T -> 3/4... wait step2 has 0.0
    # step1=0.15->T, step2=0.0->F, step3=0.25->T, step5=0.35->T -> 3/4=0.75
    assert fracs["competition"] == 0.75, f"Expected 0.75, got {fracs['competition']}"


def test_gate_pass():
    fracs = {"introductory": 0.5, "interview": 0.3, "competition": 0.25}
    assert assert_gate(fracs, threshold=0.10) is True


def test_gate_fail():
    fracs = {"introductory": 0.5, "interview": 0.1, "competition": 0.05}
    assert assert_gate(fracs, threshold=0.10) is False


def test_detect_nonzero():
    assert detect_nonzero(0.5) is True
    assert detect_nonzero(0.0) is False
    assert detect_nonzero(0.001) is True


def test_save_results():
    fracs = {"introductory": 0.6, "interview": 0.4, "competition": 0.25}
    with tempfile.TemporaryDirectory() as tmpdir:
        out = f"{tmpdir}/reward_fractions.json"
        result = save_results(fracs, out)
        assert result["gate_result"] == "PASS"
        assert result["monotonicity_holds"] is True
        loaded = json.loads(Path(out).read_text())
        assert loaded["gate_result"] == "PASS"


def test_compute_step_series():
    series = compute_step_series(SAMPLE_RECORDS)
    assert "steps" in series
    assert len(series["steps"]) == len(SAMPLE_RECORDS)
    assert "introductory" in series
    assert "competition" in series


if __name__ == "__main__":
    test_load_reward_log()
    test_compute_nonzero_fractions()
    test_gate_pass()
    test_gate_fail()
    test_detect_nonzero()
    test_save_results()
    test_compute_step_series()
    print("All tests passed")
