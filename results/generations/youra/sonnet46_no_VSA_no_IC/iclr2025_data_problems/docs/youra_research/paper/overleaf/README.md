# Overleaf LaTeX Project — Phase 6.5.1 Output

**Paper:** Which Pile Domains Drive Which Benchmarks? Domain Exposure Trajectory Analysis of Pythia  
**Format:** ICML 2025  
**Generated:** 2026-08-21 by Anonymous Research Pipeline (YouRA)

## Quick Start (Overleaf)

1. Upload the entire `overleaf/` folder to a new Overleaf project
2. Set `main.tex` as the main document
3. Set compiler to **pdfLaTeX**
4. Compile: BibTeX → pdfLaTeX → pdfLaTeX

## Local Compilation

```bash
cd paper/overleaf/
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

## Project Structure

```
overleaf/
├── main.tex                  # Main document (ICML 2025 format)
├── references.bib            # BibTeX bibliography
├── icml2025.sty              # ICML 2025 style file
├── icml2025.bst              # ICML 2025 bibliography style
├── output.pdf                # Compiled PDF
├── sections/
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── methodology.tex
│   ├── experiments.tex
│   ├── results.tex
│   ├── discussion.tex
│   ├── conclusion.tex
│   └── appendix.tex
└── figures/
    ├── fig1_domain_proxy_comparison.png
    ├── fig2_focal_violins.png
    ├── fig3_tukey_heatmap.png
    ├── fig4_proxy_scatter.png
    ├── gate_metrics.png
    ├── trajectories.png
    ├── variance_heatmap.png
    └── spearman_matrix.png
```

## Before Submission Checklist

- [ ] Replace author name/affiliation placeholders in `main.tex`
- [ ] Add acknowledgements section
- [ ] Verify all `\cite{}` keys resolve correctly
- [ ] Check figure placements in two-column layout
- [ ] Run spellcheck
- [ ] Verify page limit compliance (ICML 2025: 9 pages + references)

## Notes

- `icml2025.sty` downloaded from official ICML 2025 style package
- 1 bibtex warning: empty journal field in `Brandfonbrener2024CoLoR` (NeurIPS preprint) — harmless
- Pipeline version: YouRA Phase 6.5.1
