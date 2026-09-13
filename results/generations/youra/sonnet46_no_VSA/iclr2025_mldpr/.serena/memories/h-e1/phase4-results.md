# h-e1 Phase 4 Results (2026-08-02)

## Gate: PASS

- n_qualified_cells_primary (>=10 papers, 2021-2023): **372** (threshold: 200)
- n_qualified_cells_fallback (>=5): 377
- n_qualified_cells_upper (>=15): 363
- Total panel cells (2015-2023): 1126
- Taxonomy stable: False (expected — tasks emerge post-2016)
- Task match rate: 48.7% (127/152 in extended whitelist; 95.5% of Koch 133 strict)
- paper_date coverage: 99.99%

## Data Source Adaptation

evaluation-tables Arrow row iteration is ~1.2s/row × 2254 rows = ~46min — infeasible.
Used pwc-archive/papers-with-abstracts.tasks field instead (576K papers, batch-loadable in ~2min).
papers-with-abstracts has paper_url, date, tasks[] — same semantics as planned approach.
Both datasets cached at ~/.cache/huggingface/datasets/.

## Output Files

- docs/youra_research/h-e1/code/results/panel.csv (1126 rows)
- docs/youra_research/h-e1/code/results/h_e1_results.json
- docs/youra_research/h-e1/code/results/taxonomy_gaps.csv
- docs/youra_research/h-e1/code/figures/{gate_metrics,panel_heatmap,task_coverage,papers_distribution}.png
- docs/youra_research/h-e1/experiment_results.json
- docs/youra_research/h-e1/04_validation.md

## Archived Parquet Data

Archived run at docs/youra_research/_archive/20260802T082355_routing_recovery/h-e1/code/results/
has df_papers_raw.parquet (576K papers) and df_linkages.parquet (300K linkages).
Phase 4 final run reused these parquets to compute the (task,year) panel.
