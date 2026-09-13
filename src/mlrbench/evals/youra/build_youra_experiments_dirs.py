#!/usr/bin/env python
"""
Build an AI-Scientist-V2-style experiments/ folder for each YouRA TEST_<task>.

Motivation
----------
The original chchenhui/mlrbench eval_hallucination.py reviews a paper with
    code_path = <task>/experiments
and combines that whole folder via read_combine_files() (no size cap).

YouRA results instead scatter code/logs/result-summaries under
    TEST_<task>/docs/youra_research/<run>/h-*/...

This script collects, for each TEST_<task>, every

    *.py   (python code)
    *.json (experiment / result summaries)
    *.log  (run logs)

found under the h-* hypothesis directories of its youra_research dir, and
copies them FLAT into

    TEST_<task>/experiments/

with a collision-safe name encoding the original relative path, e.g.

    20260317_buildingtrust__h-e1__code__main.py

so that a downstream reviewer can do code_path=TEST_<task>/experiments and
read_combine_files() it exactly like the original MLR-Bench flow.

Exclusion rules mirror read_combine_h_dirs() in mlrbench/mlrbench/utils/utils.py:
noise dirs (cache, .omc, __pycache__, outputs, data, ...) are skipped, and the
results.md / results.json sentinel files are dropped.

Default is DRY-RUN (prints what it would do). Pass --write to actually copy.
"""
import argparse
import os
import os.path as osp
import shutil
import sys

# Extensions to collect (the user-requested subset of the MLR-Bench default).
COLLECT_EXTS = (".py", ".json", ".log")

# Files always dropped, matching read_combine_files() in utils.py.
SKIP_FILENAMES = {"results.md", "results.json"}

# Directory names pruned while walking, matching read_combine_h_dirs()'s
# exclude_dirs + its extra search-exclude set in utils.py.
EXCLUDE_DIRS = {
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    "outputs",
    "data",
    "experiment_results",
    ".omc",
    ".data_cache",
    "cache",
    "figures",
    "adapters",
    "_archive",
    "paper",
    "papers",
    "01_round_table",
    # h-*/code/tests/ unit tests are not part of the experiment code to review.
    "tests",
    # Tool caches: huge, generated, not real experiment code.
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".hypothesis",
    ".ipynb_checkpoints",
    "node_modules",
    ".tox",
    ".coverage",
    "htmlcov",
    ".egg-info",
}


def find_research_dir(test_dir):
    """Return TEST_<task>/docs/youra_research if it exists, else None."""
    research_dir = osp.join(test_dir, "docs", "youra_research")
    return research_dir if osp.isdir(research_dir) else None


def find_h_dirs(research_dir):
    """Return the list of h-* hypothesis directories under research_dir.

    Same traversal logic as read_combine_h_dirs(): stop descending once an
    h-* directory is found, prune EXCLUDE_DIRS everywhere else.
    """
    if osp.basename(osp.normpath(research_dir)).startswith("h-"):
        return [research_dir]

    h_dirs = []
    for root, dirs, _ in os.walk(research_dir):
        dirs.sort()
        if root != research_dir and osp.basename(root).startswith("h-"):
            h_dirs.append(root)
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    return sorted(h_dirs)


def collect_files(h_dir):
    """Yield absolute paths of files to copy from within a single h-* dir."""
    for root, dirs, files in os.walk(h_dir):
        dirs.sort()
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in sorted(files):
            if fname in SKIP_FILENAMES:
                continue
            if not fname.endswith(COLLECT_EXTS):
                continue
            yield osp.join(root, fname)


def flat_name(research_dir, src_path):
    """Encode src_path's path-relative-to-research_dir into a flat filename.

    e.g. <research>/20260317_buildingtrust/h-e1/code/main.py
      -> 20260317_buildingtrust__h-e1__code__main.py
    """
    rel = osp.relpath(src_path, research_dir)
    return rel.replace(os.sep, "__")


def _copy_with_cap(src, dst, max_file_bytes):
    """Copy src->dst. If max_file_bytes is set and src is larger, copy only
    the first max_file_bytes bytes and append a truncation marker.

    Generated logs / result dumps can be multi-MB of repeated progress bars
    or tracebacks that blow past every model's context window. Capping per
    file at build time keeps the experiments/ folder reviewable while
    preserving the head of the file (initial setup / first errors).
    """
    size = os.path.getsize(src)
    if max_file_bytes is None or size <= max_file_bytes:
        shutil.copy2(src, dst)
        return False
    with open(src, "rb") as fin:
        head = fin.read(max_file_bytes)
    with open(dst, "wb") as fout:
        fout.write(head)
        marker = (
            f"\n\n[TRUNCATED by build_youra_experiments_dirs.py: "
            f"kept first {max_file_bytes} of {size} bytes "
            f"({size - max_file_bytes} bytes omitted)]\n"
        )
        fout.write(marker.encode("utf-8", errors="replace"))
    return True


def build_for_test_dir(test_dir, write=False, clean=False, max_file_bytes=None):
    """Build TEST_<task>/experiments for one test_dir. Returns file count."""
    research_dir = find_research_dir(test_dir)
    if research_dir is None:
        print(f"[SKIP] {test_dir}: no docs/youra_research")
        return 0

    h_dirs = find_h_dirs(research_dir)
    if not h_dirs:
        print(f"[SKIP] {test_dir}: no h-* directories under {research_dir}")
        return 0

    out_dir = osp.join(test_dir, "experiments")
    if clean and osp.isdir(out_dir):
        if write:
            shutil.rmtree(out_dir)
            print(f"  [CLEAN] removed existing {out_dir}")
        else:
            print(f"  [DRY] would remove existing {out_dir}")

    planned = []  # (src, dst)
    seen = {}
    for h_dir in h_dirs:
        for src in collect_files(h_dir):
            name = flat_name(research_dir, src)
            # Defensive: guarantee uniqueness even if encoding ever collides.
            if name in seen and seen[name] != src:
                stem, ext = osp.splitext(name)
                i = 1
                while f"{stem}__{i}{ext}" in seen:
                    i += 1
                name = f"{stem}__{i}{ext}"
            seen[name] = src
            planned.append((src, osp.join(out_dir, name)))

    print(
        f"[{test_dir}] {len(h_dirs)} h-dir(s), "
        f"{len(planned)} file(s) -> {out_dir}"
    )

    oversized = [
        (src, os.path.getsize(src))
        for src, _ in planned
        if max_file_bytes is not None and os.path.getsize(src) > max_file_bytes
    ]

    if write:
        os.makedirs(out_dir, exist_ok=True)
        n_trunc = 0
        for src, dst in planned:
            if _copy_with_cap(src, dst, max_file_bytes):
                n_trunc += 1
        msg = f"  [DONE] copied {len(planned)} files"
        if n_trunc:
            msg += f" ({n_trunc} truncated at {max_file_bytes} bytes)"
        print(msg)
    else:
        for src, dst in planned[:8]:
            tag = ""
            if max_file_bytes is not None and os.path.getsize(src) > max_file_bytes:
                tag = f"  [TRUNC -> {max_file_bytes}B of {os.path.getsize(src)}B]"
            print(f"  [DRY] {osp.relpath(src)}  ->  {osp.basename(dst)}{tag}")
        if len(planned) > 8:
            print(f"  [DRY] ... and {len(planned) - 8} more")
        if oversized:
            print(f"  [DRY] {len(oversized)} file(s) exceed {max_file_bytes}B "
                  f"and would be truncated:")
            for src, sz in sorted(oversized, key=lambda x: -x[1]):
                print(f"        {sz:>10d}B  {osp.relpath(src)}")

    return len(planned)


# The 10 sonnet45 tasks live in suffix-less TEST_<task> dirs; the opus45
# variants live in TEST_<task>_opus45[_N]. These presets let you build one
# set without touching the other.
SONNET45_TASKS = [
    "bi_align",
    "buildingtrust",
    "data_problems",
    "dl4c",
    "mldpr",
    "question",
    "scope",
    "scsl",
    "verifiai",  # on-disk misspelling of canonical task key "verifai"
    "wsl",
]

# The sonnet46 run uses the same suffix-less TEST_<task> dirs and the same
# 10 task keys as sonnet45 (only the papers/results dir differs), so the
# directory-selection preset is identical. Alias kept separate for clarity.
SONNET46_TASKS = SONNET45_TASKS


def discover_test_dirs(
    root,
    only_tasks=None,
    include_copies=False,
    exclude=None,
    exact_names=None,
):
    """List TEST_* dirs with a youra_research folder.

    - Skips "copy"/" copy 2" duplicates unless include_copies.
    - only_tasks: keep dirs whose name CONTAINS any of these task keys.
    - exclude: drop dirs whose name CONTAINS any of these substrings
      (e.g. "opus45"). Applied after only_tasks.
    - exact_names: if given, keep ONLY dirs whose name exactly equals one of
      these (overrides only_tasks substring matching). Used by the sonnet45
      preset so TEST_scsl matches but TEST_scsl_opus45 does not.
    """
    exclude = exclude or []
    out = []
    for name in sorted(os.listdir(root)):
        if not name.startswith("TEST_"):
            continue
        path = osp.join(root, name)
        if not osp.isdir(path):
            continue
        if not include_copies and "copy" in name.lower():
            continue
        if not osp.isdir(osp.join(path, "docs", "youra_research")):
            continue
        if exact_names is not None:
            if name not in exact_names:
                continue
        elif only_tasks and not any(t in name for t in only_tasks):
            continue
        if any(x in name for x in exclude):
            continue
        out.append(path)
    return out


def _parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--root",
        default=".",
        help="Workspace root containing TEST_* dirs (default: cwd)",
    )
    p.add_argument(
        "--write",
        action="store_true",
        help="Actually copy files (default: dry-run)",
    )
    p.add_argument(
        "--clean",
        action="store_true",
        help="Remove an existing experiments/ before rebuilding",
    )
    p.add_argument(
        "--tasks",
        nargs="*",
        default=None,
        help="Only build TEST_* dirs whose name contains one of these "
        "keys (e.g. buildingtrust scsl). Default: all.",
    )
    p.add_argument(
        "--exclude",
        nargs="*",
        default=None,
        help="Drop TEST_* dirs whose name contains any of these substrings "
        "(e.g. opus45). Applied after --tasks/--variant.",
    )
    p.add_argument(
        "--variant",
        choices=["sonnet45", "sonnet46", "opus45", "all"],
        default="all",
        help=(
            "Preset: 'sonnet45'/'sonnet46' = the 10 suffix-less TEST_<task> "
            "dirs only (excludes *_opus45); both resolve the same dirs since "
            "sonnet45 and sonnet46 share the TEST_<task> layout. "
            "'opus45' = only TEST_*_opus45* dirs; "
            "'all' = no preset filter (default)."
        ),
    )
    p.add_argument(
        "--include-copies",
        action="store_true",
        help="Also process 'TEST_x copy 2' style duplicate dirs",
    )
    p.add_argument(
        "--max-file-bytes",
        type=int,
        default=300_000,
        help="Per-file size cap in bytes. Files larger than this are copied "
        "truncated (head kept + a marker) so giant generated logs / result "
        "dumps don't blow the reviewer's context window. 0 = no cap "
        "(original MLR-Bench behavior). Default: 300000 (~300KB).",
    )
    return p.parse_args()


def main():
    args = _parse_args()
    root = osp.abspath(args.root)
    if not osp.isdir(root):
        print(f"[FATAL] root not found: {root}")
        sys.exit(1)

    exclude = list(args.exclude or [])
    exact_names = None
    only_tasks = args.tasks

    if args.variant in ("sonnet45", "sonnet46"):
        # Exactly TEST_<task> for the 10 tasks; no _opus45, no copies.
        # sonnet45 and sonnet46 share the same suffix-less TEST_<task> dirs
        # and task keys, so the same exact-name set applies to both.
        tasks = SONNET45_TASKS if args.variant == "sonnet45" else SONNET46_TASKS
        exact_names = {f"TEST_{t}" for t in tasks}
        if "opus45" not in exclude:
            exclude.append("opus45")
    elif args.variant == "opus45":
        # Only dirs whose name contains "opus45". If the user also passed
        # --tasks, require both (substring match handles that downstream).
        only_tasks = list(only_tasks or []) + ["opus45"]

    test_dirs = discover_test_dirs(
        root,
        only_tasks=only_tasks,
        include_copies=args.include_copies,
        exclude=exclude,
        exact_names=exact_names,
    )
    if not test_dirs:
        print(f"No TEST_* dirs with docs/youra_research under {root}")
        sys.exit(0)

    max_file_bytes = args.max_file_bytes if args.max_file_bytes > 0 else None

    mode = "WRITE" if args.write else "DRY-RUN"
    print(f"Mode: {mode} | variant: {args.variant} | root: {root} | "
          f"{len(test_dirs)} TEST dir(s)")
    print(f"Collecting extensions: {', '.join(COLLECT_EXTS)}")
    print(f"Per-file cap: "
          f"{max_file_bytes if max_file_bytes else 'none (no cap)'}")
    if not args.write:
        print("(dry-run: nothing is copied; re-run with --write to apply)\n")

    total = 0
    for test_dir in test_dirs:
        total += build_for_test_dir(
            test_dir,
            write=args.write,
            clean=args.clean,
            max_file_bytes=max_file_bytes,
        )

    print(f"\n{'Copied' if args.write else 'Would copy'} {total} file(s) "
          f"across {len(test_dirs)} TEST dir(s).")


if __name__ == "__main__":
    main()
