# Overleaf LaTeX Project

**Paper:** Directed Citation Asymmetry in the huashen218 Bidirectional Alignment Corpus: Pipeline Validation and Preliminary Measurement

**Generated:** 2026-08-21 by Anonymous Research Pipeline — Phase 6.5.1

## Compilation Instructions

### Local (TeX Live)
```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Overleaf
1. Zip this folder: `zip -r overleaf.zip overleaf/`
2. Upload to Overleaf: New Project → Upload Project
3. Add `icml2025.sty` from https://icml.cc/Conferences/2025/StyleAuthorInstructions
4. Set compiler to pdfLaTeX
5. Compile

## Structure

```
overleaf/
├── main.tex              # Main document
├── references.bib        # BibTeX references (4 entries, 100% verified)
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
    ├── fig1_gate_metrics.png
    ├── fig2_dropout_by_venue.png
    ├── fig3_edge_heatmaps.png
    ├── fig4_venue_pie.png
    └── corpus_overview.png
```

## Note on ICML Style

`main.tex` uses `\usepackage{icml2025}`. Without `icml2025.sty`, it falls back to standard `article` class with `natbib`. The fallback compiles cleanly and produces a readable PDF. Download the official style file from the ICML 2025 website for submission-ready formatting.
