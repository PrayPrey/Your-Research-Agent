# `analysis/` — Experiment Reproduction and Paper Artifacts

Scripts and bundled outputs that regenerate the tables and figures in the paper
from the evaluation results under [`../results/`](../results/README.md).

> **Before running any script here, install the `mlrbench-youra` package in
> editable mode from the repository root** (`pip install -e .`) so that
> `python -m mlrbench.evals.*` and the scripts in this folder can import it.
> See [`../src/README.md`](../src/README.md) for details. Scripts that call
> judge APIs load `OPENROUTER_API_KEY` from the repository-root `.env`.

## Folder Guide

| Folder | Contents |
|:--|:--|
| [`LLM_as_Judge_main/`](LLM_as_Judge_main/) | Pairwise LLM-as-judge evaluation scripts and results (YouRA vs baselines), plus Fleiss' kappa aggregation. |
| [`Data_type_fabrication_analysis/`](Data_type_fabrication_analysis/) | Real/Synthetic/Fabricated data-provenance diagnostics over papers and their experiment folders. |
| [`MLRbench_scores_analysis/`](MLRbench_scores_analysis/) | MLR-Bench score table construction (Table 1) and the ablation-study score statistics. |
| [`MLRbench_hallucination_analysis/`](MLRbench_hallucination_analysis/) | Hallucination prevalence/taxonomy/evidence-intersection figures. |
| [`MLRbench_hallucination_human_eval/`](MLRbench_hallucination_human_eval/) | Human validation of AI-judge hallucination flags with inter-rater reliability (details [below](#human-validation-of-hallucination-flags-mlrbench_hallucination_human_eval)). |
| [`VSA/`](VSA/) | Recovery-routing telemetry analysis (routing-level CSVs and stacked-bar figure). |

## Verifying the Statistics Quoted in the Author Responses

Five self-contained checkers recompute, from the raw outputs bundled in this
repository, every statistic quoted in the discussion-period author responses.
Each script is standard-library only, locates the repository root by walking
up from its own location (so it runs from any working directory in a fresh
clone), prints one `[PASS]`/`[FAIL]` line per claim with the recomputed and
quoted values side by side, and exits 0 iff everything passes. Each script
also saves its full report to a `verify_*_results.txt` file next to itself;
the bundled result files contain the committed run, carry no timestamps, and
are reproduced byte-identically by re-running the script.

| Script | Verifies (161 checks in total, all passing) |
|:--|:--|
| [`MLRbench_scores_analysis/verify_score_claims.py`](MLRbench_scores_analysis/verify_score_claims.py) | The persistence-versus-context (no-VSA) ablation table (all means/SDs/deltas), the 8/10 task direction with its exact paired permutation test (p = 0.092) and sign test (p = 0.109), the per-task transitions (dl4c 3.75 -> 2.50, question 2.25 -> 4.25, wsl 3.00 -> 4.50) and the single high Grok-4.3 scores behind the two exceptions, the MLR-Agent Sonnet 4.5 reference (Overall 3.10), the YouRA-vs-MLR-Agent contrast (+1.10, permutation p = 0.059), the six Table 1 first-place cells, and the Sonnet 4.6 scsl trace numbers (ratio 8.8, AUC 0.914) in the released artifacts. |
| [`LLM_as_Judge_main/verify_pairwise_claims.py`](LLM_as_Judge_main/verify_pairwise_claims.py) | All six Table 2 win/tie/lose rows and the aggregates (72/33/15 vs MLR-Agent, 55/38/27 vs AI Scientist V2) recounted from the raw per-judge verdicts; the task-level 5 wins/5 ties/0 losses for the focal comparison with its sign test (p = 0.063); Fleiss' kappa recomputed from scratch for all six cells and cross-checked against `fleiss_kappa_summary.csv` (fair-to-moderate in five of six; -0.02 for YouRA vs MLR-Agent on Sonnet 4.6). |
| [`MLRbench_hallucination_human_eval/verify_human_eval_claims.py`](MLRbench_hallucination_human_eval/verify_human_eval_claims.py) | Overall flag precision 203/270 = 75.2% with Wilson 95% CI 69.7-80.0; the four per-category precisions; per-system precision (68/90, 70/90, 65/90) with chi-square(2) = 0.75, p = 0.686; anchor reliability 69/90 = 76.7% with Cohen's kappa = 0.54; the 18-of-21 one-directional disagreements; and the YouRA-subset agreement 26/30 with kappa = 0.72. |
| [`VSA/verify_routing_claims.py`](VSA/verify_routing_claims.py) | The routing telemetry: 28/40/18 = 86 archive-producing recovery events across the three backbones; 81 reset / 5 redesign / 0 unclassified; and that the two longest Sonnet 4.5 trajectories by archived recovery events are dl4c and question. |
| [`Data_type_fabrication_analysis/verify_provenance_claims.py`](Data_type_fabrication_analysis/verify_provenance_claims.py) | The data-provenance diagnostic over the three main lanes (3 systems x 3 backbones x 10 tasks, two analyzers): every cell of the paper's real-data-classification table (both-analyzer, Opus 4.6, and GPT-5.4 counts), the per-analyzer totals (27/12/18 and 28/12/18 for YouRA / MLR-Agent / AI Scientist V2), the conservative both-analyzer totals (27/11/17), analyzer agreement on 85 of 90 cells, and the single MLR-Agent Fabricated case. |

```bash
python analysis/MLRbench_scores_analysis/verify_score_claims.py
python analysis/LLM_as_Judge_main/verify_pairwise_claims.py
python analysis/MLRbench_hallucination_human_eval/verify_human_eval_claims.py
python analysis/VSA/verify_routing_claims.py
python analysis/Data_type_fabrication_analysis/verify_provenance_claims.py
```

## Pairwise Judging (`LLM_as_Judge_main/`)

The pairwise script loads `.env`, can prompt interactively if paths are omitted,
and uses explicit paths for reproducibility. `--judge-model` accepts only the
four supported judges: `google/gemini-3.1-pro-preview`, `openai/gpt-5.4`,
`x-ai/grok-4.3`, `anthropic/claude-opus-4.6`.

```bash
# Compare two papers. By default this runs both A/B and B/A orderings.
python analysis/LLM_as_Judge_main/run_llm_as_judge.py \
    --paper-a path/to/youra.md \
    --paper-b path/to/baseline.pdf \
    --task path/to/task.md \
    --label-a YouRA \
    --label-b "AI Scientist V2" \
    --judge-model google/gemini-3.1-pro-preview \
    --output analysis/LLM_as_Judge_main/custom_results.json

# Validate prompts and file loading without calling the judge API
python analysis/LLM_as_Judge_main/run_llm_as_judge.py \
    --paper-a path/to/youra.md \
    --paper-b path/to/baseline.pdf \
    --task path/to/task.md \
    --output analysis/LLM_as_Judge_main/dry_run_results.json \
    --dry-run
```

Aggregate judge CSVs and compute Fleiss' kappa:

```bash
python analysis/LLM_as_Judge_main/compute_fleiss_kappa.py \
    --input-dir analysis/LLM_as_Judge_main/LLM_as_Judge_results/LLM_as_Judge_YouRA_vs_MLRagent \
    --input-dir analysis/LLM_as_Judge_main/LLM_as_Judge_results/LLM_as_Judge_YouRA_vs_AI_scientist_v2 \
    --output analysis/LLM_as_Judge_main/fleiss_kappa_summary.csv \
    --format csv
```

## Data-Provenance Diagnostics (`Data_type_fabrication_analysis/`)

These scripts load `.env`. The Claude-backed runner requires an authenticated
Claude Code CLI session; the Codex-backed runner requires an authenticated Codex
CLI session. Both explore the experiment folder with the agent's built-in
file-listing, file-reading, and code-search tools; no MCP servers are required.
No Python packages beyond the base `mlrbench-youra` install are needed.

To re-run the diagnostic over the bundled benchmark generations
(`results/generations/{youra,mlragent,ai_scientist_v2}` x
`{sonnet45,opus45,sonnet46}` x the ten MLR-Bench tasks, ablation lanes
excluded), use the driver script; it resolves the per-system layouts
automatically and skips pairs whose output JSON already exists, so an
interrupted batch can simply be re-run:

```bash
cd analysis/Data_type_fabrication_analysis

# Preview the resolved (paper, experiment) pairs without running anything
python run_generations_data_type.py --engine both --dry-run

# Full batch: 90 pairs per engine, sequential
python run_generations_data_type.py --engine claude   # Claude Code CLI, claude-opus-4-6
python run_generations_data_type.py --engine codex    # Codex CLI, gpt-5.4
python run_generations_data_type.py --engine both

# Subsets
python run_generations_data_type.py --engine claude --systems youra --backbones sonnet45
python run_generations_data_type.py --engine codex --names bi_align scsl
```

Per-system path resolution used by the driver: the paper is
`docs/youra_research/*/paper/refinement/06_paper_refinement.md` (YouRA, the
same refined manuscript version used for MLR-Judge scoring),
`iclr2025_<name>.pdf` (AI Scientist V2), or `results/paper_*.md` (MLR-Agent);
the experiment folder is always the task's `experiments/` subfolder. Results
are written to
`data_type_analysis_results/generations_{claude,codex}/<system>_<backbone>/iclr2025_<name>_fabrication_analysis_data_type.json`.

Underneath, each pair runs one of the two single-pair runners below.
Each runner supports two modes:

- **Single-pair mode** (free-form paths): pass `--paper-file`, `--exp-folder`,
  `--output-json` to analyze one arbitrary (paper, experiment-folder) pair.
- **Batch mode** (MLR-Bench layout): pass `--paper-dir`, `--exp-dir`,
  `--output-dir`, and the runner iterates over names matching
  `iclr2025_<name>.md`/`iclr2025_<name>/`. `--names` selects which names to
  process (default: the bundled ten MLR-Bench tasks).

```bash
# Single-pair mode (Claude) — arbitrary paper/experiment paths
python analysis/Data_type_fabrication_analysis/run_fabrication_grounded_claude_data_type.py \
    --paper-file path/to/my_paper.md \
    --exp-folder path/to/my_experiment_dir \
    --output-json path/to/out/my_paper_fabrication_analysis_data_type.json \
    --model claude-opus-4-6

# Single-pair mode (Codex)
python analysis/Data_type_fabrication_analysis/run_fabrication_grounded_codex_data_type.py \
    --paper-file path/to/my_paper.md \
    --exp-folder path/to/my_experiment_dir \
    --output-json path/to/out/my_paper_fabrication_analysis_data_type.json \
    --model gpt-5.4 \
    --cwd .

# Batch mode (Claude) — MLR-Bench iclr2025_<name> layout
python analysis/Data_type_fabrication_analysis/run_fabrication_grounded_claude_data_type.py \
    --paper-dir path/to/generated_papers \
    --exp-dir path/to/experiment_folders \
    --output-dir analysis/Data_type_fabrication_analysis/data_type_analysis_results/generations_claude/youra_sonnet45 \
    --model claude-opus-4-6 \
    --names scsl wsl

# Batch mode (Codex)
python analysis/Data_type_fabrication_analysis/run_fabrication_grounded_codex_data_type.py \
    --paper-dir path/to/generated_papers \
    --exp-dir path/to/experiment_folders \
    --output-dir analysis/Data_type_fabrication_analysis/data_type_analysis_results/generations_codex/youra_sonnet45 \
    --model gpt-5.4 \
    --cwd . \
    --names scsl wsl
```

The pie-chart script uses the fixed result root
`analysis/Data_type_fabrication_analysis/data_type_analysis_results/` and writes
both PNG and PDF outputs next to the script:

```bash
python analysis/Data_type_fabrication_analysis/make_data_type_pies.py
```

## Score Tables (`MLRbench_scores_analysis/`)

```bash
# Reproduces the main MLR-Bench score table (Table 1 / the "End-to-End Scores"
# table in the top-level README).
# Outputs: analysis/MLRbench_scores_analysis/overall/table1_mlrbench_overall_scores.{csv,tex}
#          and table1_task_level_scores.csv
python analysis/MLRbench_scores_analysis/overall/build_overall_score_table.py
```

The Table 1 caption and Main Results also quote paired significance tests for
the Overall-score gaps across the 30 matched `(backbone, task)` cells. Those
numbers are regenerated by:

```bash
# Reads results/evaluations/mlrbench_overall_score/{youra,mlragent,ai_scientist_v2}/
# and writes analysis/MLRbench_scores_analysis/paired_overall_tests_results.json.
# Cell score = mean of the four judges' Overall.score values for one
# (backbone, task) pair; the paired sign-flip test uses B=100,000 and seed 42.
python analysis/MLRbench_scores_analysis/paired_overall_tests.py
```

The bundled result file reports YouRA's Overall advantage as +0.85 over
MLR-Agent (`p = 0.006` after rounding) and +0.64 over AI Scientist V2
(`p = 0.044` after rounding), matching the values quoted in the paper.

### Ablation-Study Score Statistics

Per-lane mean / sample-SD statistics for every ablation lane bundled under
`results/evaluations/mlrbench_overall_score/youra_ablation_study/`
(`sonnet45_no_VSA`, `sonnet45_no_IC`, `sonnet45_no_mcp`,
`sonnet45_no_reflection`, `sonnet46_no_VSA`, `sonnet46_no_IC`,
`sonnet46_no_mcp`, `sonnet46_no_reflection`, `opus45_no_VSA`,
`opus45_no_IC`, `opus45_no_mcp`, `opus45_no_reflection`).
Aggregation matches Table 1:
scores are averaged over the four judges within each task, then mean ± sample
SD is taken across the ten tasks.

```bash
# CSV-only output to analysis/MLRbench_scores_analysis/ablation_score_stats/:
#   <lane>_task_level_scores.csv        one row per (task, judge)
#   youra_ablation_study_summary.csv    one row per lane (mean & SD per metric)
python analysis/MLRbench_scores_analysis/build_ablation_score_stats.py
```

The appendix ablation tests use the same matched-cell design as the main
Overall significance tests. For each component, the script compares full YouRA
against the matching ablated run across the 30 `(backbone, task)` cells, then
tests pairwise contrasts between component drop sizes:

```bash
# Writes analysis/MLRbench_scores_analysis/paired_ablation_tests_results.json.
python analysis/MLRbench_scores_analysis/paired_ablation_tests.py
```

The accompanying notebook
[`MLRbench_scores_analysis/ablation_score_stats_analysis.ipynb`](MLRbench_scores_analysis/ablation_score_stats_analysis.ipynb)
regenerates the CSVs (its first cell runs the script), recomputes the statistics
independently from those CSVs, cross-checks them against the summary CSV, and
adds a per-judge breakdown. Both the script and the notebook are standard-library
only and locate the repository root themselves, so they run from any working
directory in a fresh clone.

For the two substitution controls (`sonnet45_no_VSA`, `sonnet45_no_IC`),
[`MLRbench_scores_analysis/compute_ablation_control_stats.py`](MLRbench_scores_analysis/compute_ablation_control_stats.py)
additionally derives the full control statistics — lane summaries, unrounded
deltas against the `sonnet45` baseline, per-task Overall direction, and the
exact paired permutation / tie-excluded sign tests — directly from the raw
judge JSONs, saving a deterministic report alongside as
`compute_ablation_control_stats_results.txt`.

## VSA Recovery-Routing Analysis (`VSA/`)

```bash
# Outputs: analysis/VSA/routing_levels{,_detail,_per_backbone,_per_task}.csv
#          and analysis/VSA/routing_levels_stack.png
python analysis/VSA/classify_routing_levels.py
python analysis/VSA/plot_routing_levels.py
```

## Hallucination Analysis (`MLRbench_hallucination_analysis/`)

```bash
# Outputs: analysis/MLRbench_hallucination_analysis/plots/*.png
python analysis/MLRbench_hallucination_analysis/extract_hallucination_csvs.py
python analysis/MLRbench_hallucination_analysis/plot_hallucination_prevalence.py
python analysis/MLRbench_hallucination_analysis/plot_hallucination_taxonomy_bounds.py
python analysis/MLRbench_hallucination_analysis/plot_hallucination_taxonomy_intersection.py
```

## Human Validation of Hallucination Flags (`MLRbench_hallucination_human_eval/`)

Inter-rater reliability bundle for the human evaluation of AI-judge
hallucination flags. Three primary annotators (A/B/C) each labeled 90
non-overlapping flags as True (real hallucination) / False (false positive) —
270 judgments in total; an anchor annotator then blindly re-judged a stratified
90-item overlap (30 per primary annotator, collected in two batches). All
annotators are anonymous (Annotator A/B/C, Anchor).

Item ids of the form `results/evaluations/...#idx` are repository-root-relative
paths into `results/evaluations/mlrbench_hallucination/`. The analysis scripts
join labels by id only (they never open those files), and the evaluation GUIs
resolve the same ids against the repository root, so everything works directly
from a fresh clone of this repository.

### Key Results

- On the 90-item overlap: agreement 69/90 = 76.7%, Cohen's kappa = 0.541
  (95% CI [0.37, 0.71], moderate)
- 18 of the 21 disagreements go in the single direction "primary True ->
  anchor False": the anchor applied a systematically stricter threshold
  rather than random label noise
- Per-system agreement: YouRA 26/30 (86.7%) > AI Scientist V2 22/30 >
  MLR-Agent 21/30
- Precision-corrected hallucination counts (total automated flags x
  human-validated per-system precision): YouRA 420 -> 317, MLR-Agent
  552 -> 429, AI Scientist V2 413 -> 298; pairwise paper-level bootstrap
  tests give p = 0.003 (YouRA vs MLR-Agent), p = 0.571 (YouRA vs
  AI Scientist V2), p < 0.001 (AI Scientist V2 vs MLR-Agent)
- Details: numeric outputs are bundled in `report_stats.json` and
  `corrected_counts_results.json`; the full `reliability_report.docx` is
  regenerated with `build_reliability_report.py` (see
  [Reproduce](#reproduce))

### File Inventory

Data:

- `labels_a/b/c_Annotator*.json` — the three primary annotators' True/False labels (90 each)
- `labels_d_anchor_1-30.json` / `labels_d1_anchor_31-90.json` — anchor re-evaluation (30 + 60 items)
- `selection_anchor_30.json` / `selection_anchor_60_batch2.json` — stratified-sampling manifests
- `selection_manifest*.csv` — CSV versions of the manifests
- `eval_gui_A/B/C.html` — the annotation GUIs shown to the primary annotators
  (also the inputs of the sampling scripts). Open them in a browser from inside
  the downloaded repository so the cross-check links to papers/code resolve.

Analysis code (Python 3; deps: scipy, python-docx):

- `reliability_analysis.py` — pairwise/pooled agreement + Cohen's kappa
- `report_stats.py` — full statistics for the report -> `report_stats.json`
- `build_reliability_report.py` — `report_stats.json` -> `reliability_report.docx`
- `corrected_counts_analysis.py` — precision-corrected hallucination counts
  per system (total automated flags from
  `results/evaluations/mlrbench_hallucination/` x human-validated per-system
  precision) with pairwise paper-level bootstrap tests (B=20,000, fixed
  seed; standard-library only) -> `corrected_counts_results.json`; the
  source of the paper's corrected-counts table
- `_build_reliability_set*.py` — stratified overlap-sample builders
  (deterministic, fixed seed; also regenerate the blind anchor GUIs
  `eval_gui_D_anchor.html` / `eval_gui_D1_anchor.html`, which are not
  bundled)

Results:

- `reliability_result.json` / `report_stats.json` /
  `corrected_counts_results.json` — numeric outputs
- `reliability_report.docx` — final report (n=90); not bundled, regenerate
  via `build_reliability_report.py`

### Reproduce

```bash
cd analysis/MLRbench_hallucination_human_eval

# Pairwise/pooled agreement and Cohen's kappa -> reliability_result.json
python reliability_analysis.py

# Full report statistics -> report_stats.json (requires scipy)
python report_stats.py

# Regenerate the results report docx (requires python-docx)
python build_reliability_report.py

# Precision-corrected counts + pairwise bootstrap tests
# -> corrected_counts_results.json (standard library only)
python corrected_counts_analysis.py
```
