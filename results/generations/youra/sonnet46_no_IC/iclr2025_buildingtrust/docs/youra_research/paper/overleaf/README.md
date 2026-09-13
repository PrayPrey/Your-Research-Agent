# Overleaf LaTeX Project

**Paper:** Trustworthiness Dimensions in LLMs Are Not Independent: A Partial Correlation Structure Driven by RLHF

**Generated:** 2026-08-04 by YouRA Phase 6.5.1

## Structure

```
overleaf/
├── main.tex              # Main document (entry point)
├── references.bib        # BibTeX bibliography (11 entries)
├── icml2025.sty          # ICML 2025 style file
├── icml2025.bst          # ICML 2025 bibliography style
├── algorithmic.sty       # Algorithm typesetting
├── algorithm.sty         # Algorithm float
├── sections/
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_experiments.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   ├── 07_conclusion.tex
│   └── 08_appendix.tex
├── figures/              # 12 PNG figures (copied from paper/figures/)
└── main.pdf              # Compiled output (10 pages)
```

## Compile Instructions

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Overleaf Upload

1. Zip the entire `overleaf/` directory
2. Upload to Overleaf as new project
3. Set compiler to **pdfLaTeX**
4. Main document: `main.tex`
