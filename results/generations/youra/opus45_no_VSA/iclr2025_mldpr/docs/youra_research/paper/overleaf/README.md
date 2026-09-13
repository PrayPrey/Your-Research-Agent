# Overleaf Project: Metadata Completeness Predicts Reproducibility

## Upload Instructions

1. Create new Overleaf project (Blank)
2. Upload all files from this folder:
   - `main.tex` (root document)
   - `references.bib`
   - `sections/*.tex` (7 section files)
   - `figures/*.png` (all figures)
3. Set main document to `main.tex`
4. For ICML submission: download `icml2025.sty` from ICML website and add `\usepackage{icml2025}` to preamble

## Structure

```
overleaf/
├── main.tex           # Root document
├── references.bib     # Bibliography
├── sections/          # LaTeX sections
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related.tex
│   ├── 03_methodology.tex
│   ├── 04_experiments.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   └── 07_conclusion.tex
└── figures/           # All PNG figures
```

## Local Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Generated: 2026-08-09
