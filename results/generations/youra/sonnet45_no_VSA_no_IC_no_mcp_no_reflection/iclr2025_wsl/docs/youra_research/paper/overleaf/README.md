# Overleaf LaTeX Project

## Overview

LaTeX project for paper: *Validating Layer-Wise Weight Tokenization for Architecture Family Classification*

Generated from `paper/06_paper_final.md` via Phase 6.5.1 automation.

## Structure

```
overleaf/
├── main.tex                    # Main document
├── references.bib              # BibTeX references
├── sections/
│   ├── 01_abstract.tex
│   ├── 02_introduction.tex
│   ├── 03_related_work.tex
│   ├── 04_methodology.tex
│   ├── 05_experiments.tex
│   ├── 06_results.tex
│   ├── 07_discussion.tex
│   ├── 08_conclusion.tex
│   └── 09_acknowledgments.tex
└── figures/                    # (empty - add figures here)
```

## Compilation

### Local (pdflatex + bibtex)

```bash
cd overleaf
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf`

### Overleaf Upload

1. Zip entire `overleaf/` directory
2. Upload to Overleaf project
3. Set compiler: pdfLaTeX
4. Main document: `main.tex`

## Customization

- **Title/Authors**: Edit `main.tex` lines 15-21
- **ICML Style**: Replace `\documentclass[11pt]{article}` with `\documentclass{icml2025}` (requires icml2025.sty)
- **Figures**: Add to `figures/` and reference via `\includegraphics{figures/filename.pdf}`

## Notes

- Uses `article` class (fallback when ICML style not installed)
- BibTeX references: 13 entries copied from 06_references.bib
- Per-layer normalization equations use `amsmath`
- Tables use `booktabs` package (toprule/midrule/bottomrule)
