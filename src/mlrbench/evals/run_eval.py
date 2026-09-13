#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import os
import os.path as osp
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True))
except ImportError:
    pass

from mlrbench.utils.utils import format_model_name, save_json
from mlrbench.lmm.lmm import create_lmm_client

SYSTEMS = ("youra", "ai_scientist_v2", "mlragent")

OVERALL_ROOT = osp.join("results", "evaluations", "mlrbench_overall_score")
HALLUC_ROOT  = osp.join("results", "evaluations", "mlrbench_hallucination")


def _import(modpath: str):
    return importlib.import_module(modpath)


def run_build(system: str, exp_dir: Path, *, write: bool = True,
              clean: bool = False, max_file_bytes: int = 300_000) -> None:
    if system == "youra":
        mod = _import("mlrbench.evals.youra.build_youra_experiments_dirs")
        mod.build_for_test_dir(
            str(exp_dir),
            write=write,
            clean=clean,
            max_file_bytes=max_file_bytes if max_file_bytes > 0 else None,
        )
    elif system == "ai_scientist_v2":
        mod = _import("mlrbench.evals.ai_scientist_v2.build_ai_scientist_experiments_dirs")
        mod.build_experiments_dir(str(exp_dir))
    elif system == "mlragent":
        print(f"[BUILD] mlragent has no build step; using exp_dir as-is.")
    else:
        raise ValueError(f"Unknown system: {system}")


def default_output_dir(system: str, kind: str, lane: str | None,
                       task_name: str) -> Path:
    root = OVERALL_ROOT if kind == "overall" else HALLUC_ROOT
    parts = [root, system]
    if lane:
        parts.append(lane)
    parts.append(task_name)
    return Path(*parts)


def _run_with_ladder(mod, *, paper_path: Path, task_file: Path,
                     code_dir: Path | None, client):
    """Dispatch overall_review or eval_hallucination through the cap ladder.

    When code_dir is provided, runs via the module's
    `review_with_code_cap_ladder` so context-length errors trigger the
    shared cap ladder (60K..600K char rungs) defined in
    `mlrbench.evals._context_protection`. When no code is supplied,
    falls back to a single `overall_review` call.
    """
    if code_dir is not None:
        return mod.review_with_code_cap_ladder(
            paper_path=str(paper_path),
            client=client,
            task_file=str(task_file),
            code_path=str(code_dir),
        )
    return mod.overall_review(
        paper_path=str(paper_path),
        client=client,
        task_file=str(task_file),
        code_path=None,
    )


def run_overall(system: str, *, paper_path: Path, task_file: Path,
                code_dir: Path | None, client, output_path: Path) -> bool:
    mod = _import(f"mlrbench.evals.{system}.overall_review")
    result = _run_with_ladder(mod, paper_path=paper_path, task_file=task_file,
                              code_dir=code_dir, client=client)
    if result is None:
        print("[FAIL] overall_review returned None")
        return False
    review, token_usage = result
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(review, str(output_path))
    print(f"[OK] overall  -> {output_path}  tokens={token_usage}")
    return True


def run_hallucination(system: str, *, paper_path: Path, task_file: Path,
                      code_dir: Path | None, client, output_path: Path) -> bool:
    mod = _import(f"mlrbench.evals.{system}.eval_hallucination")
    result = _run_with_ladder(mod, paper_path=paper_path, task_file=task_file,
                              code_dir=code_dir, client=client)
    if result is None:
        print("[FAIL] eval_hallucination returned None")
        return False
    review, token_usage = result
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(review, str(output_path))
    print(f"[OK] halluc   -> {output_path}  tokens={token_usage}")
    return True


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Unified runner: build (if needed) + overall_review + eval_hallucination."
    )
    p.add_argument("--system", required=True, choices=SYSTEMS,
                   help="Which method's evals to dispatch to.")
    p.add_argument("--exp-dir", required=True, type=Path,
                   help="Experiment folder for a single task.")
    p.add_argument("--task-file", required=True, type=Path,
                   help="Path to the task description (.md/.yaml/.txt).")
    p.add_argument("--paper-file", required=True, type=Path,
                   help="Path to the paper (.md or .pdf).")
    p.add_argument("--evaluator", required=True,
                   help="Judge/evaluator model id (passed to create_lmm_client).")
    p.add_argument("--output-dir", type=Path, default=None,
                   help="If given, write outputs under this dir directly. "
                        "If omitted, derive results/evaluations/mlrbench_{overall_score,hallucination}/<system>/[<lane>/]<task>/.")
    p.add_argument("--lane", default=None,
                   help="Backbone/writer lane label used only for the default output path "
                        "(e.g. sonnet45, opus45). Ignored when --output-dir is set.")
    p.add_argument("--task-name", default=None,
                   help="Task identifier used in the default output path (default: basename of --exp-dir).")
    p.add_argument("--code-dir", type=Path, default=None,
                   help="Override the code folder fed to the reviewers. "
                        "Defaults to <exp-dir>/experiments after build.")
    p.add_argument("--no-build", action="store_true",
                   help="Skip the build_*_experiments_dirs step.")
    p.add_argument("--no-code", action="store_true",
                   help="Run review without any code context.")
    p.add_argument("--skip-overall", action="store_true",
                   help="Skip overall_review.")
    p.add_argument("--skip-hallucination", action="store_true",
                   help="Skip eval_hallucination.")
    p.add_argument("--max-tokens", type=int, default=8192 * 2,
                   help="max_tokens passed to create_lmm_client.")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    exp_dir   = args.exp_dir.resolve()
    task_file = args.task_file.resolve()
    paper     = args.paper_file.resolve()

    for label, path in [("exp-dir", exp_dir), ("task-file", task_file), ("paper-file", paper)]:
        if not path.exists():
            print(f"[FATAL] --{label} does not exist: {path}", file=sys.stderr)
            return 2

    if not args.no_build:
        print(f"[BUILD] system={args.system} on {exp_dir}")
        run_build(args.system, exp_dir, write=True, clean=False)
    else:
        print("[BUILD] skipped (--no-build)")

    if args.code_dir is not None:
        code_dir: Path | None = args.code_dir.resolve()
    elif args.no_code:
        code_dir = None
    else:
        code_dir = exp_dir / "experiments"
        if not code_dir.is_dir():
            print(f"[WARN] expected code dir not found: {code_dir} (continuing without code).")
            code_dir = None

    evaluator_folder = format_model_name(args.evaluator)
    task_name = args.task_name or exp_dir.name

    print(f"[CLIENT] evaluator={args.evaluator} (folder={evaluator_folder})")
    client = create_lmm_client(model_name=args.evaluator, max_tokens=args.max_tokens, judge_mode=True)

    out_root = args.output_dir.resolve() if args.output_dir else None

    overall_out = (
        out_root / f"review_{evaluator_folder}.json"
        if out_root else
        default_output_dir(args.system, "overall", args.lane, task_name)
            / f"review_{evaluator_folder}.json"
    )
    halluc_out = (
        out_root / f"review_hallucination_{evaluator_folder}.json"
        if out_root else
        default_output_dir(args.system, "hallucination", args.lane, task_name)
            / f"review_hallucination_{evaluator_folder}.json"
    )

    ok = True
    if not args.skip_overall:
        ok &= run_overall(args.system, paper_path=paper, task_file=task_file,
                          code_dir=code_dir, client=client, output_path=overall_out)
    else:
        print("[SKIP] overall_review (--skip-overall)")

    if not args.skip_hallucination:
        ok &= run_hallucination(args.system, paper_path=paper, task_file=task_file,
                                code_dir=code_dir, client=client, output_path=halluc_out)
    else:
        print("[SKIP] eval_hallucination (--skip-hallucination)")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
