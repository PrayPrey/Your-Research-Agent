# Overleaf LaTeX Project

This folder contains the LaTeX source for the paper:

**Title:** Quality-First or Diversity-First? Compositional Ordering Effects in Sequential Data Curation for Foundation Models

## Contents

- `main.tex` — Main document, loads all sections and figures
- `sections/` — LaTeX section files (01–08)
  - 01_abstract.tex
  - 02_introduction.tex
  - 03_related_work.tex
  - 04_methodology.tex
  - 05_experimental_setup.tex
  - 06_results.tex
  - 07_discussion.tex
  - 08_conclusion.tex
- `figures/` — PNG figures (3 total)
  - fig_1_coefficient_trajectories.png
  - fig_2_ordering_effects.png
  - fig_3_interaction_plot.png
- `references.bib` — BibTeX bibliography
- `icml2025.sty` — ICML 2025 style file
- `icml2025.bst` — Bibliography style file

## Compilation

Run the following commands in this directory:

```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

The compiled PDF will be `main.pdf`.

## Upload to Overleaf

1. Create new Overleaf project (upload ZIP)
2. Upload all files preserving directory structure
3. Set main document to `main.tex`
4. Compile (should auto-detect pdfLaTeX + BibTeX)

## Notes

- ICML 2025 style file (`icml2025.sty`) is a compatibility shim
- Bibliography uses natbib-compatible author-year format
- Figures referenced via labels (fig:coefficient_trajectories, etc.)
- All sections are modular for easy editing
