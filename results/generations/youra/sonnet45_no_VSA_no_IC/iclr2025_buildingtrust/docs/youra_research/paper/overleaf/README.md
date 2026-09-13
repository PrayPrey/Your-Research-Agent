# ICML 2025 Submission: Sparse Coupling in LLM Trustworthiness Dimensions

This directory contains the LaTeX source for the paper "Sparse Coupling in LLM Trustworthiness Dimensions" in ICML 2025 format.

## Structure

- `main.tex` - Main document entry point
- `sections/` - Individual section files (00_abstract through 07_conclusion)
- `figures/` - All 9 figures (PNG format)
- `references.bib` - BibTeX bibliography
- `icml2025.sty` - ICML 2025 style file

## Compilation

Standard LaTeX compilation with BibTeX:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf`

## Sections

1. **Abstract** (00_abstract.tex)
2. **Introduction** (01_introduction.tex)
3. **Related Work** (02_related.tex)
4. **Methodology** (03_methodology.tex)
5. **Experiments** (04_experiments.tex)
6. **Results** (05_results.tex)
7. **Discussion** (06_discussion.tex)
8. **Conclusion** (07_conclusion.tex)

## Figures

- `difficulty_independence.png` - Correlation heatmap (difficulty vs dimensions)
- `partial_vs_raw_phi.png` - Scatter plot (partial vs raw phi)
- `quartile_stratified_phi.png` - Quartile-stratified coupling
- `heatmap_gpt-4.png` - GPT-4 coupling matrix
- `heatmap_claude-3-sonnet.png` - Claude-3 coupling matrix
- `heatmap_llama-3-70b.png` - Llama-3 coupling matrix
- `effect_size_retention.png` - Retention bar chart
- `significance_scatter.png` - Significance scatter plot
- `gate_metrics.png` - Gate metrics summary

## Notes

- Anonymous submission (author names redacted)
- Total word count: ~6,280 words
- ICML 2025 two-column format with standard page limits
- All tables use `booktabs` package for professional formatting
- Math notation uses standard LaTeX constructs
