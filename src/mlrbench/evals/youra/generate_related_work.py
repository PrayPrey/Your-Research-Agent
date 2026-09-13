"""Split a References section out of generated proposals into related_work.md.

In both bundled YouRA lanes (sonnet45, opus45) the proposal prompt does not
ask for a References list, and every bundled related_work.md is a final
artifact of the original pipeline: an API-based formatter over the "Key
Related Work" section of the 02a_extended_hypothesis_full.md files, which are
not bundled in this repository. This script therefore normally reports every
task as already split and modifies nothing.

It is retained as the third pipeline step for completeness: if a regenerated
proposal.md ever carries a "## References" section (e.g. from a modified
prompt), running this script splits that section out into related_work.md and
removes it from proposal.md. It makes no API calls.

Usage:
    python generate_related_work.py [--lane sonnet45|opus45]  # split if needed
    python generate_related_work.py --verify                  # structural check only
"""

import argparse
import re
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ROOT = REPO_ROOT / "results" / "generations" / "idea_and_proposal" / "youra"
LANES = ("sonnet45", "opus45")


def extract_references_section(proposal_content: str) -> Optional[str]:
    """Extract the References section from the generated proposal."""
    patterns = [
        r'^##\s*References\s*\n(.*?)(?=\n##|\Z)',
        r'^#\s*References\s*\n(.*?)(?=\n#|\Z)',
        r'^References:?\s*\n(.*?)(?=\n##|\n#|\Z)',
    ]
    for pattern in patterns:
        match = re.search(pattern, proposal_content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if match:
            return "## References\n\n" + match.group(1).strip()
    return None


def remove_references_section(proposal_content: str) -> str:
    """Remove the References section from the proposal content."""
    patterns = [
        r'\n##\s*References\s*\n.*',
        r'\n#\s*References\s*\n.*',
        r'\n^References:?\s*\n.*',
    ]
    for pattern in patterns:
        modified = re.sub(pattern, '', proposal_content,
                          flags=re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if modified != proposal_content:
            return modified.rstrip() + '\n'
    return proposal_content


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = data.decode("utf-8", errors="replace")
    return text.replace("\r\n", "\n")


def iter_task_dirs(root: Path, only):
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        if only and d.name not in only:
            continue
        yield d


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lane", choices=LANES, default="sonnet45")
    parser.add_argument("--root", type=Path, default=None,
                        help="Folder holding one subfolder per task (default: bundled <lane> folder)")
    parser.add_argument("--task", action="append", help="Only process this task (repeatable)")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite an existing related_work.md when proposal.md still has references")
    parser.add_argument("--verify", action="store_true",
                        help="Only check that every proposal is split (no files are modified)")
    args = parser.parse_args()
    args.root = args.root or DEFAULT_ROOT / args.lane

    if not args.root.is_dir():
        raise SystemExit(f"Task root not found: {args.root}")

    split = already = missing = warned = 0
    for d in iter_task_dirs(args.root, args.task):
        proposal_file = d / "proposal.md"
        related_file = d / "related_work.md"
        if not proposal_file.exists():
            missing += 1
            continue
        proposal = read_text(proposal_file)
        references = extract_references_section(proposal)

        if references is None:
            if related_file.exists():
                already += 1
            else:
                warned += 1
                print(f"[WARN] {d.name}: proposal.md has no References section and no related_work.md")
            continue

        if args.verify:
            warned += 1
            print(f"[UNSPLIT] {d.name}: proposal.md still contains a References section")
            continue

        if related_file.exists() and not args.force:
            warned += 1
            print(f"[WARN] {d.name}: related_work.md exists but proposal.md still has references "
                  "(use --force to re-split)")
            continue

        related_file.write_text(references.strip() + "\n", encoding="utf-8")
        proposal_file.write_text(remove_references_section(proposal), encoding="utf-8")
        split += 1
        print(f"[SPLIT] {d.name}")

    label = "verify" if args.verify else "run"
    print(f"{label}: split={split} already-split={already} no-proposal={missing} warnings={warned}")


if __name__ == "__main__":
    main()
