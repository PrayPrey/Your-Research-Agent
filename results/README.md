# `results/` — Evaluation Outputs and Generated Research Artifacts

```text
results/
+-- evaluations/    # Judge scores over the generated papers
+-- generations/    # The generated research artifacts themselves
```

## `evaluations/` Layout

```text
results/evaluations/
+-- mlrbench_overall_score/
|   +-- youra/<backbone>/                 # Main-table lanes: sonnet45, opus45, sonnet46
|   +-- youra_ablation_study/<lane>/      # Component-ablation lanes (see below)
|   +-- ai_scientist_v2/<backbone>/
|   +-- mlragent/<backbone>/
+-- mlrbench_hallucination/
|   +-- youra/<lane>/ , ai_scientist_v2/... , mlragent/...
+-- mlrbench_idea_proposal_score/
    +-- YouRA/{idea,proposal}/ , MLRBench/{idea,proposal}/
```

Within a lane, each judge has one batch folder holding one JSON per task:

```text
<lane>/reviews_<judge>_..._with_code/iclr2025_<task>/review_<judge>.json
```

Each `review_<judge>.json` contains the five rubric scores (Clarity, Novelty,
Soundness, Significance, Overall — each `{score, strengths, weaknesses}`) plus a
1–5 confidence value. The four judges are `gpt-5.4`,
`gemini-3.1-pro-preview`, `grok-4.3`, and `claude-opus-4.6` throughout.

### Ablation Study (`mlrbench_overall_score/youra_ablation_study/`)

Overall-review scores for the YouRA component-ablation conditions, each lane
with 4 judges × 10 tasks = 40 review JSONs. Each condition below has an
`opus45_`, `sonnet45_`, and `sonnet46_` lane:

| Lane (per backbone) | Ablated component |
|:--|:--|
| `*_no_VSA` | Persistence-versus-context control: no durable verification-state files; equivalent state passed through prompt-visible context. |
| `*_no_IC` | Independent-controller control: the GPT-5.2 controller route is disabled; controller-owned lifecycle/recovery decisions and debate/review moderation run from predefined static prompts. |
| `*_no_mcp` | MCP tool stack removed. |
| `*_no_reflection` | Reflection routing disabled. |
| `*_no_VSA_no_IC` | Combined control: no-VSA and controller-off applied together (`YOURA_no_VSA_no_IC/`). |
| `*_no_VSA_no_IC_no_mcp` | Combined control: no-VSA, controller-off, and no-MCP applied together. |
| `*_no_VSA_no_IC_no_mcp_no_reflection` | Combined control: all four substitutions applied together (`YOURA_no_VSA_no_IC_no_MCP_no_Reflection/`). |

Per-lane mean/SD statistics can be regenerated with
[`../analysis/README.md`](../analysis/README.md#ablation-study-score-statistics)
(`analysis/MLRbench_scores_analysis/build_ablation_score_stats.py` and the
accompanying notebook).

## `generations/` Layout

Benchmark-generation artifacts are mirrored under
`results/generations/<system>/<lane>/iclr2025_<task>/`. For YouRA lanes each
task folder contains:

```text
iclr2025_<task>/
+-- docs/youra_research/<run>/    # Full research-pipeline trace (see below)
+-- experiments/                  # Flat copy of experiment code/logs/results
|                                 # (what the with-code judges read)
+-- .serena/                      # Orchestrator project memory
```

The per-run research trace follows the standard YouRA layout:

```text
docs/youra_research/<run>/
+-- 00_brainstorm_session.md
+-- 01_targeted_research.md
+-- 01_targeted_research_full.md
+-- 02_synthesis.yaml
+-- 02b_verification_plan.md
+-- 03_refinement.md
+-- 03_refinement.yaml
+-- verification_state.yaml
+-- <h-id>/                       # One folder per sub-hypothesis
|   +-- 02c_experiment_brief.md
|   +-- 03_prd.md
|   +-- 03_architecture.md
|   +-- 03_logic.md
|   +-- 03_config.md
|   +-- 04_validation.md
|   +-- 04_checkpoint.yaml
|   +-- code/
+-- 045_validated_hypothesis.md
+-- paper/
    +-- 06_paper.md
    +-- sections/
    +-- 06_references.bib
    +-- 06_paper_final.md
    +-- review/065_review_summary.md
    +-- refinement/
        +-- 06_paper_refinement.md        -> final refined manuscript
        +-- overleaf_refinement/main.pdf  -> compiled paper PDF, when available
```

**Final generated paper:** the final refined manuscript is
`06_paper_refinement.md` inside the run's `paper/refinement/` directory.
Example:

```text
results/generations/youra/sonnet45/iclr2025_buildingtrust/docs/youra_research/2026_buildingtrust/paper/refinement/06_paper_refinement.md
```

### YouRA Lanes

| Lane | Condition |
|:--|:--|
| `sonnet45`, `opus45`, `sonnet46` | Full system per backbone (main-table runs). |
| `sonnet45_no_VSA` | Persistence-versus-context control: the task model neither reads nor writes durable verification-state files; equivalent state is supplied as prompt-visible context, while harness-side shadow files (`.ablation_shadow/`) preserve identical stage transitions. |
| `sonnet45_no_IC` | Independent-controller control: the GPT-5.2 controller route is disabled; controller-owned lifecycle and recovery decisions, plus debate and review moderation, run from predefined static prompts, while debate itself is conducted by the execution model. |
| `*_no_mcp` | MCP tool stack removed. |
| `*_no_reflection` | Reflection routing disabled. |
| `*_no_VSA_no_IC` | Combined control: both the no-VSA and the controller-off substitutions applied in one run. |
| `*_no_VSA_no_IC_no_mcp` | Combined control: no-VSA, controller-off, and no-MCP in one run. |
| `*_no_VSA_no_IC_no_mcp_no_reflection` | Combined control: all four substitutions in one run. |

Every ablation condition exists for all three backbones (`opus45_*`,
`sonnet45_*`, `sonnet46_*`).

### `generations/idea_and_proposal/` (Idea/Proposal-Stage Artifacts)

Idea- and proposal-stage outputs scored in
`evaluations/mlrbench_idea_proposal_score/` (paper Tables 13-14), organized as
`generations/idea_and_proposal/<system>/<lane>/<task>/` plus one shared task
folder:

```text
generations/idea_and_proposal/
+-- tasks/<task>.md      # Original MLR-Bench task descriptions (201 tasks)
+-- youra/{sonnet45,opus45}/<task>/
+-- mlragent/{sonnet45,opus45}/<task>/
```

Both YouRA lanes share one layout: each task folder bundles the generated
artifacts and the source documents they were derived from:

```text
<task>/
+-- task.md                       # Original MLR-Bench task description (copy)
+-- 00_brainstorm_session.md      # YouRA Phase 0 brainstorm (provenance)
+-- 01_targeted_research.md       # YouRA Phase 1 targeted-research report (provenance)
+-- 02_hypothesis_generation.md   # YouRA Phase 2A Extended hypothesis (bundled copy
|                                 # of the pipeline's 02a_extended_hypothesis.md)
+-- idea.md                       # 200-word research idea
+-- prompt.txt                    # Prompt that produces proposal.md (verbatim record)
+-- proposal.md                   # Generated research proposal
+-- related_work.md               # Formatted related-work list (final artifact)
```

The idea-conversion prompt was recorded for one task (sonnet45
`iclr2023_bands`, bundled as `idea_prompt.txt`; that task ships no
`prompt.txt`); the proposal prompt is bundled for the other 401 task folders.
`related_work.md` came from an API-based formatter over the "Key Related
Work" section of the pipeline's `02a_extended_hypothesis_full.md` files,
which are not bundled, so it is a final artifact in both lanes. The
MLR-Agent lanes bundle `idea.md`, `proposal.md`, and `related_work.md`. The
bundled judge reviews cover 196-201 tasks per lane and stage (a few judge
calls did not return a complete review).

#### Regenerating idea.md / proposal.md / related_work.md

Run from the repository root after `pip install -e .`, in this order:

```bash
export OPENROUTER_API_KEY=...   # or put it in a .env file
python src/mlrbench/evals/youra/generate_research_ideas.py       # 1) idea.md
python src/mlrbench/evals/youra/generate_proposals_from_llm.py   # 2) proposal.md
python src/mlrbench/evals/youra/generate_related_work.py         # 3) normally a no-op (see below)
```

All three scripts take `--lane sonnet45|opus45` (default `sonnet45`) and a
`--verify` mode that makes no API calls. For the first two scripts `--verify`
rebuilds every prompt from the source documents and compares it against the
bundled `idea_prompt.txt` / `prompt.txt`: every bundled prompt matches
byte-for-byte (401 proposal prompts across both lanes, plus the one recorded
idea prompt); the remaining idea prompts were not saved by the original
pipeline, so those `idea.md` files cannot be byte-verified and are
regenerated with the same template. Without `--verify` the scripts fill in
missing outputs only, and `--force` regenerates existing ones (the proposal
script replays the bundled `prompt.txt` verbatim unless `--rebuild-prompt`
is given). Step 3 is normally a no-op: the proposal prompt asks for no
References section and `related_work.md` is a final artifact in both lanes;
the script only splits a References section if a regenerated proposal ever
contains one.

#### Re-running the idea/proposal judge reviews

The stage reviews behind `evaluations/mlrbench_idea_proposal_score/` can be
re-run over the bundled artifacts (one judge call per task and stage):

```bash
python src/mlrbench/evals/youra/review_idea.py        [--lane sonnet45|opus45]
python src/mlrbench/evals/youra/review_proposal.py    [--lane sonnet45|opus45]
python src/mlrbench/evals/mlragent/review_idea.py     [--lane sonnet45|opus45]
python src/mlrbench/evals/mlragent/review_proposal.py [--lane sonnet45|opus45]
```

Each script reviews `idea.md` against the task description, or `proposal.md`
against the task description, `idea.md`, and `related_work.md`, using the
MLR-Bench stage rubrics, and writes one JSON per task into the matching
`reviews_<judge>_..._{idea,proposal}` folder. Tasks whose review JSON already
exists are skipped (`--force` replaces them; `--task <name>` restricts the
run). The paper's judge id `google/gemini-3-pro-preview` is the default but
has been retired by OpenRouter; pass
`--evaluator google/gemini-3.1-pro-preview` (or another supported judge) to
re-run today. A different judge id writes into its own `reviews_<judge>_...`
folder, leaving the bundled scores untouched; note that the aggregation
scripts under `analysis/` glob review folders by lane and stage, so keep only
one judge folder per lane in place when regenerating paper statistics.

### Anonymization Note

Local filesystem paths inside logs, configs, and pipeline documents have been
anonymized for release: the workspace root is rewritten to `/workspace` and the
home directory to `/home/anonymous`. LaTeX build byproducts and credential-style
files were removed; the remaining `.env.example` files contain placeholders
only.
