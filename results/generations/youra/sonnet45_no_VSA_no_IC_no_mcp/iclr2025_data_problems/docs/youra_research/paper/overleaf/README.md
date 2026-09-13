# Overleaf Project: Transfer Stability Taxonomy

This directory contains the LaTeX source for the ICML 2025 submission.

## Project Structure

```
overleaf/
├── main.tex                      # Main LaTeX document
├── icml2025.sty                  # ICML 2025 style file
├── references.bib                # BibTeX bibliography
├── sections/                     # Section files
│   ├── 01_abstract.tex
│   ├── 02_introduction.tex
│   ├── 03_related_work.tex
│   ├── 04_methodology.tex
│   ├── 05_experimental_setup.tex
│   ├── 06_results.tex
│   ├── 07_discussion.tex
│   ├── 08_conclusion.tex
│   └── 09_references.tex
└── figures/                      # Figure files
    ├── curation_impact_chart.png
    ├── gate_metrics_comparison.png
    ├── threshold_sensitivity_heatmap.png
    └── transfer_delta_barchart.png
```

## Compilation

Standard LaTeX workflow:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or use the compilation script (if available):

```bash
./compile.sh
```

## Upload to Overleaf

1. Create a new blank project on Overleaf
2. Upload all files maintaining the directory structure
3. Set main document to `main.tex`
4. Compile (Overleaf auto-detects pdflatex + bibtex workflow)

## Source

Generated from Phase 6.5.1 (Overleaf Conversion) of the YOURA research pipeline.

- Source Markdown: `paper/06_paper_final.md`
- Source Bibliography: `paper/06_references.bib`
- Source Figures: `paper/figures/*.png`
- Conversion Date: 2026-08-24
