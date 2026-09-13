# Overleaf LaTeX Project

**Paper:** Per-Sample Hessian Trace as an Annotation-Free Minority Group Proxy Under ERM Training

## Structure

```
overleaf/
├── main.tex              # Root document
├── references.bib        # BibTeX references
├── sections/
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related.tex
│   ├── 03_methodology.tex
│   ├── 04_experiments.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   └── 07_conclusion.tex
└── figures/              # All PNG figures
```

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Overleaf Upload

1. Zip the entire `overleaf/` folder
2. Upload to Overleaf as a new project
3. Set compiler to pdfLaTeX
4. For ICML 2025 submission: download `icml2025.sty` from https://icml.cc/Conferences/2025/StyleAuthorInstructions and add to project root, then replace `\documentclass[10pt,twocolumn]{article}` with the ICML preamble
