# `src/` — Modified MLR-Bench Evaluation Utilities

This directory contains the `mlrbench-youra` package (`src/mlrbench`), a modified
version of the [MLR-Bench](https://github.com/chchenhui/mlrbench) evaluation code.
It is used for **evaluation only**, not for launching the YouRA research loop.
The package provides unified judge wrappers for YouRA, AI Scientist V2, and
MLR-Agent outputs.

## Setup

Install the repository in editable mode from the repository root:

```bash
pip install -e .
```

The evaluator reads `OPENROUTER_API_KEY` from `.env`, so no separate shell
`export` is needed when running from the repository root.

## Single-Task Evaluation

Use the unified runner for overall quality and hallucination/factuality review:

```bash
python -m mlrbench.evals.run_eval \
    --system youra \
    --exp-dir TEST_scsl \
    --task-file path/to/task.md \
    --paper-file path/to/paper.md \
    --evaluator google/gemini-3.1-pro-preview \
    --lane sonnet45 \
    --task-name scsl
```

Supported systems are:

```text
youra
ai_scientist_v2
mlragent
```

Unless `--output-dir` is provided, outputs are written under:

```text
results/evaluations/mlrbench_overall_score/
results/evaluations/mlrbench_hallucination/
```

See [`../results/README.md`](../results/README.md) for the layout of these
output folders and of the bundled evaluation results.

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

Run without `--write` to preview the files that would be copied.

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
paper path, evaluator model, and output directory through CLI flags.
