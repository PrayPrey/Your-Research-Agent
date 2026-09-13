#!/usr/bin/env python3
"""
run_phase_refine.py — Refine paper using Claude Code CLI

Refines the final paper (06_paper_final.md) into a polished, neutral, objective
third-person version, using the research directory as ground truth.

Pipeline integration:
  run_total_youra.py --enable-refine
    └─ run_post_experiment.py --enable-refine
         └─ run_phase_refine.py --research-folder <path>

Standalone:
  python run_phase_refine.py --research-folder docs/youra_research/20260317_bi_align
  python run_phase_refine.py --research-folder <path> --timeout 1800

Output:
  {research_folder}/paper/refinement/06_paper_refinement.md
  {research_folder}/paper/refinement/overleaf_refinement/main.pdf

Exit codes:
  0 — Refinement completed successfully
  1 — Fatal error

Author: Anonymous
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from phase_output_verifier import build_claude_cmd
from md_to_pdf import convert as md_to_pdf_convert

# ============================================================
# Path Configuration
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
PROJECT_DIR = SCRIPT_DIR.parent.parent
CLAUDE_CLI = Path.home() / ".local" / "bin" / "claude"

LOG_FILE = CACHE_DIR / "run_phase_refine.log"


# ============================================================
# Logging
# ============================================================
def log(message: str):
    """Log to file and stderr."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [REFINE] {message}"
    print(entry, file=sys.stderr)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass


# ============================================================
# Prompt loading
# ============================================================
PROMPTS_DIR = SCRIPT_DIR / "tone_prompts"
PROMPT_FILE = PROMPTS_DIR / "refine.md"


def get_prompt() -> str:
    """Load the refine prompt template."""
    if not PROMPT_FILE.exists():
        print(f"ERROR: Prompt file not found: {PROMPT_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


# ============================================================
# CLI
# ============================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="Refine paper using Claude Code CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --research-folder docs/youra_research/20260304_scsl
  %(prog)s --research-folder <path> --timeout 1800
        """,
    )

    parser.add_argument(
        "--research-folder", type=str, required=True,
        help="Path to research folder containing paper/06_paper_final.md",
    )
    parser.add_argument(
        "--timeout", type=int, default=1800,
        help="Max runtime in seconds (default: 1800 = 30 minutes)",
    )

    return parser.parse_args()


# ============================================================
# Main
# ============================================================
def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    args = parse_args()

    research_folder = str(Path(args.research_folder).resolve())

    # Validate research folder
    if not Path(research_folder).exists():
        log(f"ERROR: Research folder does not exist: {research_folder}")
        sys.exit(1)

    # Validate paper exists
    paper_path = os.path.join(research_folder, "paper", "06_paper_final.md")
    if not os.path.isfile(paper_path):
        log(f"ERROR: paper/06_paper_final.md not found — Phase 6.5 must complete first")
        sys.exit(1)

    # Create output directory
    output_dir = os.path.join(research_folder, "paper", "refinement")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "06_paper_refinement.md")

    log("=" * 60)
    log(f"Paper Refinement starting")
    log(f"  Research folder: {research_folder}")
    log(f"  Paper path:      {paper_path}")
    log(f"  Output path:     {output_path}")
    log(f"  Timeout:         {args.timeout}s")
    log("=" * 60)

    # Build prompt from external file
    prompt = get_prompt().format(
        exp_dir=research_folder,
        paper_path=paper_path,
        output_path=output_path,
    )

    # Determine Claude CLI path
    claude_bin = str(CLAUDE_CLI) if CLAUDE_CLI.exists() else "claude"

    log(f"[1/3] Calling Claude Code CLI (REFINE mode)...")

    start_time = time.time()

    env = os.environ.copy()
    env.pop("CLAUDECODE", None)

    try:
        claude_cmd = build_claude_cmd(
            CLAUDE_CLI, prompt,
            extra_flags=["--allowedTools", "Read,Glob,Grep,Write", "--output-format", "text"],
        )
        result = subprocess.run(
            claude_cmd,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            cwd=os.path.dirname(research_folder),
            env=env,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        log(f"TIMEOUT after {elapsed:.0f}s")
        sys.exit(1)

    elapsed = time.time() - start_time

    if result.returncode != 0:
        log(f"ERROR: Claude CLI exited with code {result.returncode} after {elapsed:.0f}s")
        if result.stderr:
            log(f"stderr: {result.stderr[:3000]}")
        sys.exit(1)

    if not os.path.isfile(output_path):
        log("ERROR: Claude did not write the output file")
        if result.stdout:
            log(f"stdout: {result.stdout[:2000]}")
        sys.exit(1)

    output_size = os.path.getsize(output_path)
    log(f"[2/3] Refinement done. Written to: {output_path}")
    log(f"      Output size: {output_size} bytes")
    log(f"      Elapsed: {elapsed:.0f}s ({elapsed / 60:.1f} min)")

    # ---- PDF Generation ----
    log(f"[3/3] Converting to LaTeX + PDF...")
    pdf_output_dir = os.path.join(output_dir, "overleaf_refinement")

    # Find figures and bib from the research folder
    figures_dir = os.path.join(research_folder, "paper", "figures")
    bib_path = os.path.join(research_folder, "paper", "06_references.bib")
    # Try to reuse ICML style files from existing Phase 6.5.1 overleaf output
    style_source = os.path.join(research_folder, "paper", "overleaf")

    pdf_success = md_to_pdf_convert(
        input_md=output_path,
        output_dir=pdf_output_dir,
        figures_dir=figures_dir if os.path.isdir(figures_dir) else None,
        bib_path=bib_path if os.path.isfile(bib_path) else None,
        style_source=style_source if os.path.isdir(style_source) else None,
    )

    if pdf_success:
        pdf_path = os.path.join(pdf_output_dir, "main.pdf")
        log(f"      PDF generated: {pdf_path}")
    else:
        log(f"      WARNING: PDF generation failed (non-fatal, Markdown output still available)")

    # Print research folder for pipeline consumption
    print(research_folder)

    log(f"Paper Refinement complete")
    log("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    main()
