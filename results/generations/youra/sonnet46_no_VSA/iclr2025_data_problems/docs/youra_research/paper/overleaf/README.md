# Overleaf LaTeX Project

**Paper:** Language-Family Retention Bias from Global CCNet Perplexity Thresholding: A Calibrated Measurement on RedPajama-V2

## Structure

```
overleaf/
├── main.tex              # Main document
├── references.bib        # BibTeX references
├── sections/             # Section files
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_experimental_setup.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   ├── 07_conclusion.tex
│   └── 08_acknowledgments.tex
└── figures/              # PNG figures
    ├── cramers_v_bar.png
    ├── perplexity_kde.png
    ├── retention_gap.png
    └── retention_heatmap.png
```

## Compilation

```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Notes

- Uses standard `article` class with `natbib` for citations
- For ICML 2025 submission: replace `\documentclass{article}` with `\documentclass{icml2025}` and add `\usepackage{icml2025}`
- ICML style files available at: https://icml.cc/Conferences/2025/StyleAuthorInstructions
