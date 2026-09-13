#!/usr/bin/env python3
"""Data-type fabrication analysis over results/generations (main lanes, no ablations).

Wraps run_fabrication_grounded_claude_data_type.py in single-pair mode with
per-system path resolution. Resume-safe: skips pairs whose output JSON exists.

Usage:
  python run_generations_data_type.py [--systems youra ai_scientist_v2 mlragent]
      [--backbones sonnet45 opus45 sonnet46] [--names bi_align ...] [--model claude-opus-4-6]
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GEN = HERE.parent.parent / "results" / "generations"
ENGINES = {
    "claude": (HERE / "run_fabrication_grounded_claude_data_type.py", "claude-opus-4-6",
               HERE / "data_type_analysis_results" / "generations_claude"),
    "codex":  (HERE / "run_fabrication_grounded_codex_data_type.py", "gpt-5.4",
               HERE / "data_type_analysis_results" / "generations_codex"),
}
NAMES = ["bi_align", "buildingtrust", "data_problems", "dl4c", "mldpr",
         "question", "scope", "scsl", "verifai", "wsl"]

def paper_for(system: str, task_dir: Path, name: str) -> Path | None:
    if system == "youra":
        hits = sorted(task_dir.glob("docs/youra_research/*/paper/refinement/06_paper_refinement.md"))
        return hits[0] if hits else None
    if system == "ai_scientist_v2":
        p = task_dir / f"iclr2025_{name}.pdf"
        return p if p.is_file() else None
    if system == "mlragent":
        hits = sorted((task_dir / "results").glob("paper_*.md"))
        return hits[0] if hits else None
    return None

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--systems", nargs="*", default=["youra", "ai_scientist_v2", "mlragent"])
    ap.add_argument("--backbones", nargs="*", default=["sonnet45", "opus45", "sonnet46"])
    ap.add_argument("--names", nargs="*", default=NAMES)
    ap.add_argument("--engine", choices=["claude", "codex", "both"], default="claude")
    ap.add_argument("--model", default=None, help="Override the engine's default model.")
    ap.add_argument("--dry-run", action="store_true", help="Resolve paths and report; run nothing.")
    args = ap.parse_args()
    engines = ["claude", "codex"] if args.engine == "both" else [args.engine]

    jobs, missing = [], []
    for engine in engines:
      RUNNER, default_model, OUT_ROOT = ENGINES[engine]
      model = args.model or default_model
      for system in args.systems:
        for bb in args.backbones:
            for name in args.names:
                task_dir = GEN / system / bb / f"iclr2025_{name}"
                if not task_dir.is_dir():
                    task_dir = GEN / system / bb / f"iclr2025_{name}_{bb}"
                paper = paper_for(system, task_dir, name)
                exp = task_dir / "experiments"
                if not (exp.is_dir() and paper):
                    missing.append(f"{engine}/{system}/{bb}/{name}")
                    continue
                out = OUT_ROOT / f"{system}_{bb}" / f"iclr2025_{name}_fabrication_analysis_data_type.json"
                jobs.append((engine, RUNNER, model, system, bb, name, paper, exp, out))

    if missing:
        print(f"MISSING ({len(missing)}): {missing}", file=sys.stderr)
    done = [j for j in jobs if j[-1].exists()]
    todo = [j for j in jobs if not j[-1].exists()]
    print(f"jobs={len(jobs)} done={len(done)} todo={len(todo)}")
    if args.dry_run:
        for engine, _r, model, system, bb, name, paper, exp, out in jobs:
            print(f"  {engine}({model})/{system}/{bb}/{name}: paper={paper.relative_to(GEN)} exp={exp.relative_to(GEN)}")
        return 0

    fails = []
    for i, (engine, runner, model, system, bb, name, paper, exp, out) in enumerate(todo, 1):
        label = f"[{i}/{len(todo)}] {engine}/{system}/{bb}/{name}"
        print(label, flush=True)
        r = subprocess.run([sys.executable, str(runner),
                            "--paper-file", str(paper),
                            "--exp-folder", str(exp),
                            "--output-json", str(out),
                            "--model", model])
        if r.returncode != 0 or not out.exists():
            fails.append(f"{engine}/{system}/{bb}/{name}")
            print(f"{label} FAILED", flush=True)
    print(f"finished; failures={len(fails)}: {fails}")
    return 1 if fails else 0

if __name__ == "__main__":
    raise SystemExit(main())
