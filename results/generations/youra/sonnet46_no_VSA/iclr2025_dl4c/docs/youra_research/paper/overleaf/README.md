# Overleaf LaTeX Project

Paper: "What Does Code SFT Actually Teach? Source Identity Governs Benchmark Performance via Distributional Alignment"

## Structure

```
overleaf/
├── main.tex              # Root LaTeX file
├── references.bib        # BibTeX references
├── sections/
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_experiments.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   └── 07_conclusion.tex
├── figures/              # All paper figures (PNG)
└── main.pdf              # Compiled output
```

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Requires: TeX Live 2025+ with `booktabs`, `natbib`, `graphicx`, `amsmath`, `times`.

## Upload to Overleaf

1. Zip the entire `overleaf/` directory
2. In Overleaf: New Project → Upload Project → select zip
3. Set compiler to pdfLaTeX
4. Compile
