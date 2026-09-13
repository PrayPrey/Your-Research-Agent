# Overleaf Project

**Title**: Permutation Equivariance as a Prerequisite for Weight-Space Learning

## Structure

```
overleaf/
├── main.tex           # Main document
├── references.bib     # Bibliography
├── sections/          # Section files
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_experiments.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   └── 07_conclusion.tex
└── figures/           # Figure files
```

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Upload to Overleaf

1. Zip entire `overleaf/` folder
2. New Project > Upload Project
3. Select zip file
