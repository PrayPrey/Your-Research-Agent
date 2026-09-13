# Overleaf LaTeX Project

**Paper:** Format-Dependent Uncertainty Quantification: Why Semantic Entropy Underperforms Simple Confidence on Multiple-Choice Hallucination Detection

**Generated:** 2026-08-29

## Structure

```
overleaf/
├── main.tex              # Main document
├── references.bib        # Bibliography
├── README.md             # This file
├── sections/
│   ├── 01_abstract.tex
│   ├── 02_introduction.tex
│   ├── 03_related.tex
│   ├── 04_methodology.tex
│   ├── 05_experiments.tex
│   ├── 06_results.tex
│   ├── 07_discussion.tex
│   └── 08_conclusion.tex
└── figures/              # Place figure files here
```

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Upload to Overleaf

1. Zip this folder
2. Upload to Overleaf as new project
3. Replace article documentclass with icml2025.sty if submitting to ICML
