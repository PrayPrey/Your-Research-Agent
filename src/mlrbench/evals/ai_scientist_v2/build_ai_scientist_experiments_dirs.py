"""
Build per-research `experiments/` folders for AI Scientist V2 (sonnet45) results,
mirroring the layout used by the original MLR-Bench repo
(chchenhui/mlrbench: ai_scientist_v2_papers/o4-mini/<task>/experiments/).

For each research folder under `experiments_sonnet45/<exp>/`, this collects:

  - every stage's best_solution_<hash>.py   (from logs/0-run/stage_*/)
  - ablation_summary.json                   (from logs/0-run/)
  - baseline_summary.json                   (from logs/0-run/)
  - research_summary.json                   (from logs/0-run/)
  - draft_summary.json                      (from logs/0-run/)
  - idea.md                                 (from the research folder root)

and copies them flat into `experiments_sonnet45/<exp>/experiments/`.

best_solution files keep their original hashed names (hashes differ per stage,
so there are no collisions). If `experiments/` already exists it is skipped
(idempotent), so re-running will not clobber a manually edited folder.

The companion evaluation script reads this folder via
`read_combine_files(code_path=.../experiments)` exactly like the original
`eval_hallucination.py`.

Usage:
    python mlrbench/evals/build_ai_scientist_experiments_dirs.py            # sonnet45 (default)
    python mlrbench/evals/build_ai_scientist_experiments_dirs.py experiments_sonnet46
"""
import glob
import os
import os.path as osp
import shutil
import sys


DEFAULT_RESULTS_DIR = "experiments_opus45"

# Summary files that live directly under logs/0-run/
SUMMARY_FILES = (
    "ablation_summary.json",
    "baseline_summary.json",
    "research_summary.json",
    "draft_summary.json",
)


def _stage_label(stage_path):
    """Extract a short stage label from a stage_* directory path.

    e.g. .../stage_3_creative_research_1_first_attempt -> "stage_3"
    """
    base = osp.basename(osp.dirname(stage_path))
    parts = base.split("_")
    if len(parts) >= 2 and parts[0] == "stage":
        return f"stage_{parts[1]}"
    return base


def collect_source_files(exp_dir):
    """Return a list of (src_path, dest_name) pairs to copy into experiments/.

    Mirrors the file set found in the original repo's experiments/ folder.
    best_solution files keep their original hashed names; only when the SAME
    hash appears in more than one stage (same best node carried forward) do we
    prefix the duplicates with their stage label so no stage is silently lost.
    """
    run_dir = osp.join(exp_dir, "logs", "0-run")
    sources = []
    missing = []

    # 1. Every stage's best_solution_<hash>.py
    best_solutions = sorted(
        glob.glob(osp.join(run_dir, "stage_*", "best_solution_*.py"))
    )
    if not best_solutions:
        missing.append("stage_*/best_solution_*.py")

    # Detect hashes that occur in more than one stage.
    name_counts = {}
    for p in best_solutions:
        name_counts[osp.basename(p)] = name_counts.get(osp.basename(p), 0) + 1

    for p in best_solutions:
        base = osp.basename(p)
        if name_counts[base] > 1:
            # Same best node carried across stages: keep all, disambiguate.
            dest_name = f"{_stage_label(p)}_{base}"
        else:
            dest_name = base
        sources.append((p, dest_name))

    # 2. The four summary JSONs under logs/0-run/
    for name in SUMMARY_FILES:
        p = osp.join(run_dir, name)
        if osp.isfile(p):
            sources.append((p, name))
        else:
            missing.append(name)

    # 3. idea.md at the research folder root
    idea = osp.join(exp_dir, "idea.md")
    if osp.isfile(idea):
        sources.append((idea, "idea.md"))
    else:
        missing.append("idea.md")

    return sources, missing


def build_experiments_dir(exp_dir):
    """Create exp_dir/experiments/ and copy the collected files in flat."""
    dest = osp.join(exp_dir, "experiments")

    if osp.isdir(dest):
        print(f"[SKIP] experiments/ already exists: {dest}")
        return

    sources, missing = collect_source_files(exp_dir)
    if missing:
        print(f"  [WARN] {osp.basename(exp_dir)}: missing {missing}")
    if not sources:
        print(f"[SKIP] No source files found for {exp_dir}; not creating experiments/")
        return

    os.makedirs(dest, exist_ok=True)
    copied = []
    for src, dest_name in sources:
        dst = osp.join(dest, dest_name)
        if osp.exists(dst):
            print(f"  [WARN] name collision, overwriting: {dest_name}")
        shutil.copy2(src, dst)
        copied.append(dest_name)

    print(f"[DONE] {dest}")
    for name in copied:
        print(f"        + {name}")


def main(results_dir=DEFAULT_RESULTS_DIR):
    if not osp.isdir(results_dir):
        print(f"[ERROR] Results directory not found: {results_dir}")
        return

    exp_dirs = sorted(
        osp.join(results_dir, d)
        for d in os.listdir(results_dir)
        if osp.isdir(osp.join(results_dir, d))
    )
    print(f"Found {len(exp_dirs)} research folders under {results_dir}/")

    for exp_dir in exp_dirs:
        print(f"\n=== {osp.basename(exp_dir)} ===")
        build_experiments_dir(exp_dir)


if __name__ == "__main__":
    rd = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RESULTS_DIR
    main(rd)
