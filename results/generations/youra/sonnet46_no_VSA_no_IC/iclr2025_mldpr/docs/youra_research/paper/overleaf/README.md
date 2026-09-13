# Overleaf LaTeX Project

**Paper:** When Does a Benchmark Saturate? Detecting Regime Shifts in ML Leaderboard Performance Variance  
**Format:** ICML 2025  
**Generated:** 2026-08-21 by Phase 6.5.1 pipeline

## Structure

```
overleaf/
├── main.tex              # Root document
├── icml2025.sty          # ICML 2025 style file
├── references.bib        # BibTeX references
├── sections/
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related.tex
│   ├── 03_methodology.tex
│   ├── 04_setup.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   └── 07_conclusion.tex
└── figures/
    └── *.png (16 figures)
```

## Compilation

```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or upload the entire `overleaf/` folder to Overleaf as a new project.

## Notes

- `icml2025.sty` must be in the same directory as `main.tex`
- All figures referenced in the tex files are in `figures/`
- Bibliography uses short cite keys (e.g., `\cite{Killick2012}`)
