# Behavioral Coupling Paper - Overleaf Project

This directory contains the LaTeX source for the paper "Behavioral Coupling as a Metric for Bidirectional Alignment in Conversational AI".

## Structure

```
overleaf/
├── main.tex                  # Main document
├── references.bib           # Bibliography
├── sections/                # Paper sections (LaTeX)
│   ├── 01_abstract.tex
│   ├── 02_introduction.tex
│   ├── 03_related_work.tex
│   ├── 04_methodology.tex
│   ├── 05_experiments.tex
│   ├── 06_results.tex
│   ├── 07_discussion.tex
│   └── 08_conclusion.tex
└── figures/                 # Figure files
    ├── diversity_scatter.png
    ├── gate_metrics.png
    └── slope_distribution.png
```

## Compilation

Compile the paper with:

```bash
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_bi_align/docs/youra_research/paper/overleaf
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

This generates `main.pdf`.

## Uploading to Overleaf

1. Create a new project on Overleaf
2. Upload all files preserving the directory structure
3. Compile using pdfLaTeX

## Conversion Notes

- Converted from Markdown (06_paper_final.md) to LaTeX
- Section labels added for cross-referencing
- Tables formatted with booktabs package
- Citations formatted with BibTeX
- Figures referenced but not embedded (PNG files in figures/)

## Requirements

- pdflatex
- bibtex
- Standard LaTeX packages: amsmath, amssymb, graphicx, booktabs, hyperref
