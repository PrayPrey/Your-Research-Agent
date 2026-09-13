#!/usr/bin/env python3
"""Verify the recovery-routing telemetry quoted in the author responses.

Checks, against the bundled routing-level CSVs (regenerable with
``classify_routing_levels.py``), the numbers cited in the discussion-period
responses:

  * 28 / 40 / 18 = 86 archive-producing recovery events across the
    Sonnet 4.5 / Opus 4.5 / Sonnet 4.6 backbones,
  * routing-level totals: 81 reset, 5 redesign, 0 unclassified,
  * the two longest Sonnet 4.5 trajectories by archived recovery events
    are dl4c and question (the two tasks used as the trajectory-level
    illustration in the persistence-ablation discussion).

Pure standard library; runs from any working directory in a fresh clone:

    python analysis/VSA/verify_routing_claims.py

Also writes the full PASS/FAIL report (no timestamps, so re-runs are
byte-identical) to a *_results.txt file next to this script.
Exit code 0 iff every check passes.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

PASS: list[str] = []
FAIL: list[str] = []
REPORT: list[str] = []


def check(name: str, got, want) -> None:
    ok = got == want
    (PASS if ok else FAIL).append(name)
    line = f"[{'PASS' if ok else 'FAIL'}] {name}: computed={got} claimed={want}"
    REPORT.append(line)
    print(line)


def main() -> int:
    with (HERE / "routing_levels.csv").open() as f:
        rows = {r["backbone"]: r for r in csv.DictReader(f)}

    check("Sonnet 4.5 archive events", int(rows["Sonnet 4.5"]["total"]), 28)
    check("Opus 4.5 archive events", int(rows["Opus 4.5"]["total"]), 40)
    check("Sonnet 4.6 archive events", int(rows["Sonnet 4.6"]["total"]), 18)
    check("total archive events", int(rows["Total"]["total"]), 86)
    check("reset total", int(rows["Total"]["reset"]), 81)
    check("redesign total", int(rows["Total"]["redesign"]), 5)
    check("unclassified total", int(rows["Total"]["unclass"]), 0)

    # Longest two Sonnet 4.5 trajectories by archived recovery events.
    per_task: Counter[str] = Counter()
    with (HERE / "routing_levels_detail.csv").open() as f:
        for r in csv.DictReader(f):
            if r["backbone"] == "Sonnet 4.5":
                per_task[r["task"]] += 1
    top2 = {t for t, _ in per_task.most_common(2)}
    check("two longest Sonnet 4.5 trajectories", sorted(top2),
          ["dl4c", "question"])

    summary = f"{len(PASS)} passed, {len(FAIL)} failed."
    report_path = HERE / (Path(__file__).stem + "_results.txt")
    report_path.write_text("\n".join(REPORT + ["", summary]) + "\n", encoding="utf-8")
    print(f"\n{summary}")
    print(f"Report saved to {report_path.name}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
