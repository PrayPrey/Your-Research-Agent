# `src/` — Modified MLR-Bench Evaluation Utilities

This directory contains the `mlrbench-youra` package (`src/mlrbench`), a modified
version of the [MLR-Bench](https://github.com/chchenhui/mlrbench) evaluation code.
It is used for **evaluation only**, not for launching the YouRA research loop.
The package provides unified judge wrappers for YouRA, AI Scientist V2, and
MLR-Agent outputs.

## Setup

Use Python 3.10 or newer. The commands below are for a Bash-compatible shell.
Clone the repository, create a virtual environment, and install the evaluation
package from the **repository root** (the directory containing `pyproject.toml`):

```bash
git clone https://github.com/PrayPrey/Your-Research-Agent.git
cd Your-Research-Agent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .

# Create the configuration file if it does not already exist.
test -f .env || cp .env.example .env
```

Edit `.env` and replace the `OPENROUTER_API_KEY` placeholder with your own key:

```dotenv
OPENROUTER_API_KEY="your-openrouter-api-key"
```

The example below uses OpenRouter and requires API access and credits for the
selected judge model. The other keys in `.env.example` are not needed for this
example. The runner loads `.env` from the repository root; an existing shell
environment variable takes precedence over the value in `.env`.

Check that the installed runner can be imported without making an API request:

```bash
python -m mlrbench.evals.run_eval --help
```

Keep the virtual environment active and run the following commands from the
repository root. Running `pip install -e .` inside `src/` fails because the
package metadata is in the parent directory.

## Single-Task Evaluation

Use the unified runner for overall quality and hallucination/factuality review.
The task, paper, and experiment files in this example are included in the clone;
running the YouRA research loop first is unnecessary. This command sends the
evaluation inputs to the judge API and writes new reviews:

```bash
# Re-score one bundled YouRA run (run from the repository root)
python -m mlrbench.evals.run_eval \
    --system youra \
    --exp-dir results/generations/youra/sonnet45/iclr2025_scsl \
    --task-file YOURA/tasks_youra/iclr2025_scsl.md \
    --paper-file results/generations/youra/sonnet45/iclr2025_scsl/docs/youra_research/2026_scsl/paper/refinement/06_paper_refinement.md \
    --evaluator google/gemini-3.1-pro-preview \
    --lane sonnet45 \
    --output-dir results/evaluations/local_runs/youra/sonnet45/iclr2025_scsl
```

The example writes `review_gemini-3.1-pro-preview.json` and
`review_hallucination_gemini-3.1-pro-preview.json` into `--output-dir`. Using a
separate directory keeps the bundled evaluation results available for comparison.
Running the command again overwrites reviews with the same filenames in that
directory. New judge responses can differ from the published scores.

`--task-name` defaults to the basename of `--exp-dir` (here `iclr2025_scsl`),
which is the task folder name the analysis scripts expect. The example reuses
the bundled `<exp-dir>/experiments/` folder. For a new YouRA run, the runner
builds this folder if it is missing; `--rebuild` rebuilds it from the hypothesis
folders. Use `--no-build` to skip building and `--code-dir` to supply an existing
code folder at another path. Check the runner's messages: if the default
`experiments/` folder is missing after the build step, it warns and continues
without code. `--no-code` explicitly selects review without code context.

Supported systems are:

```text
youra
ai_scientist_v2
mlragent
```

To write outputs in the bundled layout instead, omit `--output-dir` and retain
`--lane`. The paths below are relative to the current working directory, so run
from the repository root. `--lane` and `--task-name` affect only this default
layout and are ignored when `--output-dir` is set:

```text
results/evaluations/mlrbench_overall_score/<system>/<lane>/reviews_<judge>_<system>_<lane>_with_code/<task>/review_<judge>.json
results/evaluations/mlrbench_hallucination/<system>/<lane>/reviews_<judge>_<system>_<lane>_with_code/<task>/review_hallucination_<judge>.json
```

YouRA ablation lanes (any `--lane` containing `_no_`, e.g. `sonnet45_no_mcp`)
are placed under `youra_ablation_study/` instead of `youra/`, matching the
bundle, so the aggregation scripts under `analysis/` pick the new reviews up.

See [`../results/README.md`](../results/README.md) for the layout of these
output folders and of the bundled evaluation results.

## Judge Context Length Limits and Truncation

We retain the MLR-Judge evaluation criteria and adapt its input handling to the
judge LLM's context length limit. For both overall and hallucination review,
each judge receives the task description, paper, and the code, result files,
and logs collected from the selected code folder. The following retry procedure
applies to **all three systems** when code context is supplied:

1. Send the input with no additional limit on the combined code, result files,
   and logs.
2. If the judge API reports that the request exceeds its context length limit,
   retry with progressively smaller caps on that combined text:
   **600,000 → 300,000 → 150,000 → 60,000 characters**. If the combined text
   exceeds a cap, keep its beginning, truncate the rest, and add a truncation
   marker. Stop at the first successful review.
3. Keep the **task description and paper in full** on every retry. If the
   request still exceeds the limit at the smallest cap, that review fails and
   no new JSON is written for it; the runner exits with a nonzero status if
   either requested review fails.

Files are concatenated in filesystem traversal order, so truncation can remove
part of a file and all subsequent files. It does **not** select the largest
files first. The caps count characters, including file headers; context-length
errors from the API trigger the retries. Overall and hallucination reviews run
this procedure independently and can succeed at different caps. Other errors
do not trigger retries at smaller caps. See
[`_context_protection.py`](mlrbench/evals/_context_protection.py) for the shared
implementation.

The YouRA experiment-folder builder also applies a separate per-file byte cap
when copying oversized files, keeping each file's beginning and appending a
marker. This preprocessing can truncate files before the first judge request.
An existing `experiments/` folder is reused as supplied. The standalone builder
exposes `--max-file-bytes` (`0` disables this preprocessing cap); see the next
section. Disabling the preprocessing cap leaves the context-error retry
procedure above active.

Input truncation due to the judge LLMs' context length limits may disadvantage
papers with extensive code, result files, or logs.

## Optional: Build `experiments/` Folders for New YouRA Runs

The bundled YouRA artifacts under `results/generations/youra/` already include
the `experiments/` folders used by the evaluation scripts. You do not need to run
this step to reproduce the included scores.

This helper is only for evaluating newly generated YouRA runs that still have the
raw `TEST_<task>/docs/youra_research/.../h-*` layout. MLR-Bench expects each task
directory to contain a flat `experiments/` folder, so the helper copies relevant
`.py`, `.json`, and `.log` files from the hypothesis folders into
`TEST_<task>/experiments/`.

```bash
python -m mlrbench.evals.youra.build_youra_experiments_dirs \
    --root path/to/workspace/with/TEST_dirs \
    --variant sonnet45 \
    --write
```

Other variants:

```bash
python -m mlrbench.evals.youra.build_youra_experiments_dirs --root path/to/workspace/with/TEST_dirs --variant sonnet46 --write
python -m mlrbench.evals.youra.build_youra_experiments_dirs --root path/to/workspace/with/TEST_dirs --variant opus45 --write
python -m mlrbench.evals.youra.build_youra_experiments_dirs --root path/to/workspace/with/TEST_dirs --variant all --write
```

Run without `--write` to preview the files that would be copied and any per-file
truncation. Use `--max-file-bytes` to change the builder's per-file cap; the
default is shown by `--help`. The unified runner uses the default cap when it
builds a YouRA `experiments/` folder.

## Package Layout

```text
src/mlrbench/
+-- evals/
|   +-- run_eval.py            # Unified CLI runner (build + overall + hallucination)
|   +-- _context_protection.py # Shared context-overflow cap ladder for large code inputs
|   +-- youra/                 # YouRA-specific reviewers + experiments-dir builder
|   +-- ai_scientist_v2/       # AI Scientist V2-specific reviewers
|   +-- mlragent/              # MLR-Agent-specific reviewers
+-- llm/, lmm/                 # Judge model client wrappers (OpenRouter/OpenAI/Anthropic)
+-- utils/                     # Shared file/reading utilities
```

The individual stage reviewers under `evals/{youra,mlragent,ai_scientist_v2}/`
are research scripts for idea, proposal, experiment, writeup, overall, and
hallucination review. `evals/youra/` also holds the three generation scripts
(`generate_research_ideas.py`, `generate_proposals_from_llm.py`,
`generate_related_work.py`) that rebuild the idea/proposal artifacts under
`results/generations/idea_and_proposal/youra/` (both the `sonnet45` and
`opus45` lanes, selected with `--lane`) from their bundled source documents, and the `review_idea.py` / `review_proposal.py` scripts in
`evals/{youra,mlragent}/` re-run the corresponding judge reviews over those
bundled artifacts; see `results/README.md` for usage. For normal reproduction, prefer
`python -m mlrbench.evals.run_eval` because it exposes the system, task path,
paper path, evaluator model, and output directory through CLI flags. Some
individual review scripts still have research-workspace paths in their
`__main__` blocks; running those modules directly requires adapting those paths.
The single-task command above supplies the paths for the public repository.
