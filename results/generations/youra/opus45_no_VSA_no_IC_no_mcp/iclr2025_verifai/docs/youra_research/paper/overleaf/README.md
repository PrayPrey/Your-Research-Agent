# Overleaf Project: Representational Alignment in Error Formatting

## Structure

```
overleaf/
├── main.tex           # Main document
├── icml2025.sty       # Style file
├── references.bib     # Bibliography
├── sections/          # LaTeX sections
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_experimental_setup.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   └── 07_conclusion.tex
└── figures/           # All figure files (.png)
```

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Upload to Overleaf

1. Create new project on Overleaf
2. Upload all files maintaining directory structure
3. Set main.tex as main document
4. Compile

## Generated

Phase 6.5.1 - 2026-08-28
