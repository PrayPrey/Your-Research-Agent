#!/usr/bin/env python3
"""Verify the data-provenance statistics quoted in the paper.

Recounts, from the bundled per-task classification JSONs under
``data_type_analysis_results/generations_{claude,codex}/<system>_<backbone>/``
(three systems x three backbones x ten MLR-Bench tasks, one JSON per task and
analyzer), every number in the paper's Data Provenance section:

  * the "Real-data classifications per system and backbone" table
    (both-analyzer count, Opus 4.6 analyzer count, GPT-5.4 analyzer count,
    each out of ten tasks),
  * the per-analyzer totals over 30 tasks (27/12/18 under Opus 4.6 and
    28/12/18 under GPT-5.4 for YouRA / MLR-Agent / AI Scientist V2) and the
    conservative both-analyzer totals (27/11/17),
  * analyzer agreement on 85 of the 90 (system, backbone, task) cells,
  * exactly one Fabricated label per analyzer (the same MLR-Agent case).

Pure standard library; runs from any working directory in a fresh clone:

    python analysis/Data_type_fabrication_analysis/verify_provenance_claims.py

Also writes the full PASS/FAIL report (no timestamps, so re-runs are
byte-identical) to a *_results.txt file next to this script.
Exit code 0 iff every check passes.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "data_type_analysis_results"

ANALYZERS = {"claude": "Opus 4.6", "codex": "GPT-5.4"}  # folder suffix -> paper name
SYSTEMS = {"youra": "YouRA", "mlragent": "MLR-Agent", "ai_scientist_v2": "AI Scientist V2"}
BACKBONES = {"sonnet45": "Sonnet 4.5", "opus45": "Opus 4.5", "sonnet46": "Sonnet 4.6"}
TASKS = ["bi_align", "buildingtrust", "data_problems", "dl4c", "mldpr",
         "question", "scope", "scsl", "verifai", "wsl"]

# Paper table: (system, backbone) -> (both analyzers, Opus 4.6, GPT-5.4) Real counts /10
TABLE_CLAIMS = {
    ("youra", "sonnet45"): (8, 8, 9),
    ("youra", "opus45"): (9, 9, 9),
    ("youra", "sonnet46"): (10, 10, 10),
    ("ai_scientist_v2", "sonnet45"): (6, 6, 6),
    ("ai_scientist_v2", "opus45"): (8, 9, 8),
    ("ai_scientist_v2", "sonnet46"): (3, 3, 4),
    ("mlragent", "sonnet45"): (1, 2, 2),
    ("mlragent", "opus45"): (4, 4, 4),
    ("mlragent", "sonnet46"): (6, 6, 6),
}
# Prose: per-analyzer Real totals over 30 tasks, and both-analyzer totals
TOTAL_CLAIMS = {
    "claude": {"youra": 27, "mlragent": 12, "ai_scientist_v2": 18},
    "codex": {"youra": 28, "mlragent": 12, "ai_scientist_v2": 18},
    "both": {"youra": 27, "mlragent": 11, "ai_scientist_v2": 17},
}
AGREEMENT_CLAIM = (85, 90)
FABRICATED_CLAIM = 1  # exactly one Fabricated label per analyzer, same cell

PASS: list[str] = []
FAIL: list[str] = []
REPORT: list[str] = []


def check(name: str, got, want) -> None:
    ok = got == want
    (PASS if ok else FAIL).append(name)
    line = f"[{'PASS' if ok else 'FAIL'}] {name}: computed={got} claimed={want}"
    REPORT.append(line)
    print(line)


def load_labels() -> dict[tuple[str, str, str, str], str]:
    """(analyzer, system, backbone, task) -> data_type label."""
    labels: dict[tuple[str, str, str, str], str] = {}
    for analyzer in ANALYZERS:
        for system in SYSTEMS:
            for backbone in BACKBONES:
                d = RESULTS / f"generations_{analyzer}" / f"{system}_{backbone}"
                files = sorted(d.glob("iclr2025_*_fabrication_analysis_data_type.json"))
                check(f"{analyzer}/{system}_{backbone} task count", len(files), len(TASKS))
                for f in files:
                    task = f.name[len("iclr2025_"):-len("_fabrication_analysis_data_type.json")]
                    labels[(analyzer, system, backbone, task)] = json.load(
                        f.open(encoding="utf-8")).get("data_type", "")
    return labels


def main() -> int:
    labels = load_labels()

    def real(analyzer: str, system: str, backbone: str) -> int:
        return sum(1 for t in TASKS if labels.get((analyzer, system, backbone, t)) == "Real")

    def both_real(system: str, backbone: str) -> int:
        return sum(1 for t in TASKS
                   if labels.get(("claude", system, backbone, t)) == "Real"
                   and labels.get(("codex", system, backbone, t)) == "Real")

    # Table: real-data classifications per system and backbone
    for (system, backbone), (want_both, want_claude, want_codex) in TABLE_CLAIMS.items():
        label = f"{SYSTEMS[system]} / {BACKBONES[backbone]}"
        check(f"{label} Real (both analyzers)", both_real(system, backbone), want_both)
        check(f"{label} Real ({ANALYZERS['claude']})", real("claude", system, backbone), want_claude)
        check(f"{label} Real ({ANALYZERS['codex']})", real("codex", system, backbone), want_codex)

    # Prose: totals over 30 tasks
    for analyzer in ("claude", "codex"):
        for system, want in TOTAL_CLAIMS[analyzer].items():
            got = sum(real(analyzer, system, b) for b in BACKBONES)
            check(f"{SYSTEMS[system]} Real /30 ({ANALYZERS[analyzer]})", got, want)
    for system, want in TOTAL_CLAIMS["both"].items():
        got = sum(both_real(system, b) for b in BACKBONES)
        check(f"{SYSTEMS[system]} Real /30 (both analyzers)", got, want)

    # Prose: analyzer agreement on 85 of 90 cells
    cells = [(s, b, t) for s in SYSTEMS for b in BACKBONES for t in TASKS]
    agree = sum(1 for (s, b, t) in cells
                if labels.get(("claude", s, b, t)) == labels.get(("codex", s, b, t)))
    check("analyzer agreement (cells)", (agree, len(cells)), AGREEMENT_CLAIM)

    # Prose: all non-real cells are Synthetic except one MLR-Agent Fabricated case
    fab = {a: sorted((s, b, t) for (aa, s, b, t), lab in labels.items()
                     if aa == a and lab == "Fabricated") for a in ANALYZERS}
    for analyzer in ANALYZERS:
        check(f"Fabricated labels ({ANALYZERS[analyzer]})", len(fab[analyzer]), FABRICATED_CLAIM)
    check("Fabricated case is the same MLR-Agent cell in both analyzers",
          fab["claude"] == fab["codex"] and all(s == "mlragent" for s, _, _ in fab["claude"]),
          True)
    other = sorted(set(labels.values()) - {"Real", "Synthetic", "Fabricated"})
    check("label vocabulary is Real/Synthetic/Fabricated only", other, [])

    summary = f"{len(PASS)} passed, {len(FAIL)} failed."
    report_path = HERE / (Path(__file__).stem + "_results.txt")
    report_path.write_text("\n".join(REPORT + ["", summary]) + "\n", encoding="utf-8")
    print(f"\n{summary}")
    print(f"Report saved to {report_path.name}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
