#!/usr/bin/env python3
"""Classify each archive snapshot into redesign / reset / unclass.

Reads raw artifacts from the trimmed repo tree:

    <repo_root>/results/generations/youra/<lane>/iclr2025_<task>[_opus45]/
        docs/youra_research/2026_<task>/_archive/<snapshot>/

Cascade (in order; first signal wins):

  STAGE 0  _ARCHIVED.md      "Route target:" / "Reason:" line
            - "Phase 0" / ROUTE_TO_0  → reset
            - "Phase 2A-Dialogue" / ROUTE_TO_2A → redesign
           (deterministic archive record written at routing time;
            highest authority — preferred whenever present)

  STAGE 1  snapshot's verification_state.yaml: episode.routing_decision

  STAGE 2  episode.termination_trigger + episode.routing_reason keywords

  STAGE 3  benchmark_metrics.failure_recording.failures_by_type counts

  STAGE 4  history fallback against the task's FINAL state yaml

  STAGE 5  unclass

Micro-repair is always 0 because it does not create an archive snapshot.

Outputs (overwrite, written next to this script):
  routing_levels.csv         lane × {redesign, reset, unclass, total}
  routing_levels_detail.csv  per-snapshot (lane, task, snapshot, level, reason)
"""
import csv
import argparse
import re
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent


def find_repo_root(start: Path) -> Path:
    """Walk up from `start` until a directory containing `results/generations/youra` is
    found. Works whether this script sits at `<repo>/VSA/`, `<repo>/analysis/`,
    `<repo>/analysis/VSA/`, etc."""
    cur = start
    while True:
        if (cur / "results" / "generations" / "youra").is_dir():
            return cur
        if cur.parent == cur:
            raise RuntimeError(
                f"Could not locate `results/generations/youra` walking up from {start}. "
                "Run this script from inside the repo tree, or set RESULTS "
                "manually."
            )
        cur = cur.parent


# (lane_folder_name, display_label, opus_suffix_required)
LANES = [
    ("sonnet45", "Sonnet 4.5", False),
    ("opus45",   "Opus 4.5",   True),
    ("sonnet46", "Sonnet 4.6", False),
]

PHASE0_PATTERNS = [r"^phase\s*0$", r"^route[d]?_to_phase_0$", r"reset"]
PHASE2A_PATTERNS = [r"^phase\s*2a", r"^2a", r"phase2a", r"dialogue", r"redesign"]

REDESIGN_REASON_KW = [
    "redesign", "mechanism", "architectural", "hypothesis revision",
    "hypothesis redesign", "phase 2a", "phase2a",
]
RESET_REASON_KW = [
    "evidence", "contradict", "unsupported", "fundamental",
    "reset", "phase 0", "phase0", "rejected",
]


# ---------- helpers --------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Classify YouRA archive routing snapshots into redesign/reset/unclass.",
    )
    parser.add_argument(
        "--results-root",
        type=Path,
        help="Path to the `results/generations/youra` directory. Defaults to auto-detecting the repo root.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repo root containing `results/generations/youra`. Ignored when --results-root is provided.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE,
        help="Directory for routing_levels*.csv outputs. Defaults to this script's directory.",
    )
    return parser.parse_args()


def resolve_results_root(args) -> Path:
    if args.results_root:
        results = args.results_root.expanduser().resolve()
    elif args.repo_root:
        results = args.repo_root.expanduser().resolve() / "results" / "generations" / "youra"
    else:
        results = find_repo_root(HERE) / "results" / "generations" / "youra"

    if not results.is_dir():
        raise RuntimeError(f"Results root does not exist or is not a directory: {results}")
    return results


def matches_any(value, patterns):
    return any(re.search(p, value, re.IGNORECASE) for p in patterns)


def normalize(s):
    return (s or "").strip().lower()


def read_field(text, key):
    m = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", text, re.MULTILINE)
    if not m:
        return None
    v = m.group(1).strip()
    if v in ("null", "~", "''", '""'):
        return None
    if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
        v = v[1:-1]
    return v


def read_text_safe(p: Path):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def task_from_dirname(name: str, opus: bool) -> str | None:
    """Parse `iclr2025_<task>` or `iclr2025_<task>_opus45`."""
    if not name.startswith("iclr2025_"):
        return None
    base = name[len("iclr2025_"):]
    if opus:
        if not base.endswith("_opus45"):
            return None
        base = base[:-len("_opus45")]
    elif base.endswith("_opus45"):
        return None
    return base


# ---------- STAGE 0 --------------------------------------------------------
def classify_from_archived_md(snap_dir: Path):
    """Stage 0: read _ARCHIVED.md.

    Two formats observed:
      (a) `*_routing_recovery` snapshots have:
            **Route target:** Phase 0          → reset
            **Route target:** Phase 2A-Dialogue → redesign
      (b) `*_reflection_recovery` snapshots have:
            **Reason:** ROUTE_TO_0 - ...        → reset
            **Reason:** ROUTE_TO_2A - ...       → redesign
    """
    marker = snap_dir / "_ARCHIVED.md"
    if not marker.is_file():
        return None
    text = read_text_safe(marker) or ""

    m = re.search(r"\*\*Route target:\*\*\s*(.+?)\s*$", text, re.MULTILINE)
    if m:
        target = normalize(m.group(1).strip("\"' "))
        if target:
            if matches_any(target, PHASE0_PATTERNS):
                return ("reset", f"_ARCHIVED.md route_target={m.group(1).strip()!r}")
            if matches_any(target, PHASE2A_PATTERNS):
                return ("redesign", f"_ARCHIVED.md route_target={m.group(1).strip()!r}")

    m = re.search(r"\*\*Reason:\*\*\s*(.+)", text)
    if m:
        reason = m.group(1).lower()
        if "route_to_0" in reason or "route_to_phase_0" in reason:
            return ("reset", "_ARCHIVED.md reason=ROUTE_TO_0")
        if "route_to_2a" in reason or "route_to_phase_2a" in reason:
            return ("redesign", "_ARCHIVED.md reason=ROUTE_TO_2A")

    return None


# ---------- STAGE 1-3 ------------------------------------------------------
def classify_from_snapshot_yaml(text):
    rd = read_field(text, "routing_decision")
    rd_n = normalize(rd)
    if rd_n:
        if matches_any(rd_n, PHASE0_PATTERNS):
            return ("reset", f"rd={rd!r}")
        if matches_any(rd_n, PHASE2A_PATTERNS):
            return ("redesign", f"rd={rd!r}")

    tt = normalize(read_field(text, "termination_trigger"))
    rr = normalize(read_field(text, "routing_reason"))
    if "must_work_partial" in tt:
        return ("redesign", f"tt={tt!r}")
    if "must_work_fail" in tt or "must_work_gate_fail" in tt or "must_work gate fail" in tt:
        if any(kw in rr for kw in REDESIGN_REASON_KW):
            return ("redesign", f"tt={tt!r}+rr-redesign")
        if any(kw in rr for kw in RESET_REASON_KW):
            return ("reset", f"tt={tt!r}+rr-reset")
        return ("reset", f"tt={tt!r}+default")

    mwp = re.search(r"must_work_partial:\s*(\d+)", text)
    mwf = re.search(r"must_work_fail:\s*(\d+)", text)
    if mwp and int(mwp.group(1)) > 0:
        return ("redesign", "fbt-partial>0")
    if mwf and int(mwf.group(1)) > 0:
        return ("reset", "fbt-fail>0")
    return None


# ---------- STAGE 4 --------------------------------------------------------
def infer_from_final(final_text):
    rd = read_field(final_text, "routing_decision")
    if rd:
        rd_n = normalize(rd)
        if matches_any(rd_n, PHASE0_PATTERNS):
            return "reset"
        if matches_any(rd_n, PHASE2A_PATTERNS):
            return "redesign"
    m = re.search(r"^\s*routing:\s*\n(?:\s+\S.*\n)*?\s+target:\s*(.+?)\s*$",
                  final_text, re.MULTILINE)
    if m:
        v = normalize(m.group(1).strip("\"'"))
        if matches_any(v, PHASE0_PATTERNS):
            return "reset"
        if matches_any(v, PHASE2A_PATTERNS):
            return "redesign"
    for key in ("stop_reason", "next_action"):
        v = normalize(read_field(final_text, key))
        if not v:
            continue
        if "phase 0" in v or "phase0" in v or "reset" in v:
            return "reset"
        if "phase 2a" in v or "phase2a" in v or "redesign" in v or "dialogue" in v:
            return "redesign"
    if re.search(r"routed_to_phase0:\s*true", final_text, re.IGNORECASE):
        return "reset"
    return None


# ---------- pipeline -------------------------------------------------------
def classify_snapshot(snap_dir: Path, final_text):
    r = classify_from_archived_md(snap_dir)
    if r:
        return r

    yaml_path = snap_dir / "verification_state.yaml"
    if yaml_path.is_file():
        text = read_text_safe(yaml_path)
        if text is not None:
            r = classify_from_snapshot_yaml(text)
            if r:
                return r
    else:
        if final_text:
            inferred = infer_from_final(final_text)
            if inferred:
                return (inferred, "final_state_fallback_no_yaml")
        return ("unclass", "no_yaml")

    if final_text:
        inferred = infer_from_final(final_text)
        if inferred:
            return (inferred, "final_state_fallback")

    return ("unclass", "no_signal")


def collect(results_root: Path):
    detail = []  # (lane_label, base, snap_name, level, reason)
    for lane_dir_name, lane_label, is_opus in LANES:
        ldir = results_root / lane_dir_name
        if not ldir.is_dir():
            continue
        for td in sorted(ldir.iterdir()):
            if not td.is_dir():
                continue
            base = task_from_dirname(td.name, is_opus)
            if base is None:
                continue
            yr = td / "docs" / "youra_research"
            if not yr.is_dir():
                continue
            for rd in yr.iterdir():
                ar = rd / "_archive"
                if not ar.is_dir():
                    continue
                final_yaml = rd / "verification_state.yaml"
                final_text = read_text_safe(final_yaml) if final_yaml.is_file() else None
                for snap in sorted(ar.iterdir()):
                    if not snap.is_dir():
                        continue
                    level, reason = classify_snapshot(snap, final_text)
                    detail.append((lane_label, base, snap.name, level, reason))
    return detail


def summarize(detail):
    counts = {label: {"micro": 0, "redesign": 0, "reset": 0, "unclass": 0}
              for _, label, _ in LANES}
    for lane_label, _, _, level, _ in detail:
        counts[lane_label][level] = counts[lane_label].get(level, 0) + 1
    return counts


TASK_ORDER = [
    "bi_align", "buildingtrust", "data_problems", "dl4c", "mldpr",
    "question", "scope", "scsl", "verifai", "wsl",
]


def per_task_matrix(detail):
    """Return dict[lane_label][task] = snapshot_count, covering every task in
    TASK_ORDER (defaulting to 0)."""
    matrix = {label: {t: 0 for t in TASK_ORDER} for _, label, _ in LANES}
    for lane_label, task, _, _, _ in detail:
        if task in matrix[lane_label]:
            matrix[lane_label][task] += 1
        else:
            matrix[lane_label][task] = matrix[lane_label].get(task, 0) + 1
    return matrix


def per_backbone_stats(matrix):
    """Per-lane row: Tasks, Total, Per task (mean), Median, Range."""
    rows = []
    for _, label, _ in LANES:
        counts = [matrix[label].get(t, 0) for t in TASK_ORDER]
        total = sum(counts)
        rows.append({
            "backbone": label,
            "tasks": len(counts),
            "total": total,
            "per_task": round(statistics.mean(counts), 1) if counts else 0,
            "median": float(statistics.median(counts)) if counts else 0,
            "range": f"{min(counts)}-{max(counts)}" if counts else "-",
            "min": min(counts) if counts else 0,
            "max": max(counts) if counts else 0,
        })
    return rows


def main():
    args = parse_args()
    results_root = resolve_results_root(args)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    detail = collect(results_root)
    counts = summarize(detail)

    out_summary = output_dir / "routing_levels.csv"
    with out_summary.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["backbone", "micro", "redesign", "reset", "unclass", "total"])
        grand = {"micro": 0, "redesign": 0, "reset": 0, "unclass": 0}
        for _, label, _ in LANES:
            c = counts[label]
            total = c["micro"] + c["redesign"] + c["reset"] + c["unclass"]
            w.writerow([label, c["micro"], c["redesign"], c["reset"], c["unclass"], total])
            for k in grand:
                grand[k] += c[k]
        w.writerow(["Total", grand["micro"], grand["redesign"], grand["reset"],
                    grand["unclass"], sum(grand.values())])

    out_detail = output_dir / "routing_levels_detail.csv"
    with out_detail.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["backbone", "task", "snapshot", "level", "classification_reason"])
        w.writerows(detail)

    print("| Backbone | micro | redesign | reset | unclass. | Total |")
    print("|---|---:|---:|---:|---:|---:|")
    grand = {"micro": 0, "redesign": 0, "reset": 0, "unclass": 0}
    for _, label, _ in LANES:
        c = counts[label]
        total = c["micro"] + c["redesign"] + c["reset"] + c["unclass"]
        print(f"| {label} | {c['micro']} | {c['redesign']} | {c['reset']} | {c['unclass']} | {total} |")
        for k in grand:
            grand[k] += c[k]
    print(f"| **Total** | **{grand['micro']}** | **{grand['redesign']}** | "
          f"**{grand['reset']}** | **{grand['unclass']}** | **{sum(grand.values())}** |")

    # ---------- Per-task matrix (task x backbone) ----------------------
    matrix = per_task_matrix(detail)
    out_per_task = output_dir / "routing_levels_per_task.csv"
    lane_labels = [label for _, label, _ in LANES]
    with out_per_task.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["task"] + lane_labels)
        col_totals = {label: 0 for label in lane_labels}
        for t in TASK_ORDER:
            row = [t]
            for label in lane_labels:
                v = matrix[label].get(t, 0)
                row.append(v)
                col_totals[label] += v
            w.writerow(row)
        w.writerow(["Total"] + [col_totals[label] for label in lane_labels])

    # ---------- Per-backbone summary stats -----------------------------
    backbone_stats = per_backbone_stats(matrix)
    out_per_backbone = output_dir / "routing_levels_per_backbone.csv"
    fields = ["backbone", "tasks", "total", "per_task", "median", "range"]
    with out_per_backbone.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in backbone_stats:
            w.writerow({k: row[k] for k in fields})

    # ---------- Per-task table (printed) -------------------------------
    print()
    print("| Task | " + " | ".join(lane_labels) + " |")
    print("|---|" + "|".join(["---:"] * len(lane_labels)) + "|")
    col_totals = {label: 0 for label in lane_labels}
    for t in TASK_ORDER:
        cells = []
        for label in lane_labels:
            v = matrix[label].get(t, 0)
            cells.append(str(v))
            col_totals[label] += v
        print(f"| {t} | " + " | ".join(cells) + " |")
    print(f"| **Total** | " + " | ".join(f"**{col_totals[label]}**" for label in lane_labels) + " |")

    # ---------- Per-backbone summary table (printed) -------------------
    print()
    print("| Backbone | Tasks | Total | Per task | Median | Range |")
    print("|---|---:|---:|---:|---:|---|")
    for r in backbone_stats:
        median_s = f"{r['median']:.1f}"
        print(f"| {r['backbone']} | {r['tasks']} | {r['total']} | "
              f"{r['per_task']} | {median_s} | {r['range']} |")

    print(f"\nWrote {out_summary}")
    print(f"Wrote {out_detail}")
    print(f"Wrote {out_per_task}")
    print(f"Wrote {out_per_backbone}")


if __name__ == "__main__":
    main()
