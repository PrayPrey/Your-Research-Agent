# Overleaf LaTeX Project

**Paper:** More Feedback, Worse Repair: An Overhead-Normalized Comparison of Formal Feedback for LLM Code Repair

## Structure

```
overleaf/
├── main.tex              # Root document
├── references.bib        # BibTeX references
├── figures/              # PNG figures (12 files)
└── sections/
    ├── 00_abstract.tex
    ├── 01_introduction.tex
    ├── 02_related_work.tex
    ├── 03_methodology.tex
    ├── 04_experimental_setup.tex
    ├── 05_results.tex
    ├── 06_discussion.tex
    ├── 07_conclusion.tex
    └── 08_appendix.tex
```

## Compilation

```bash
cd overleaf/
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Requires: pdflatex, bibtex (TeX Live or MiKTeX). No special style files needed (uses standard `article` class).

## Overleaf Upload

Zip the entire `overleaf/` directory and upload to Overleaf as a new project. Set the compiler to pdfLaTeX.
