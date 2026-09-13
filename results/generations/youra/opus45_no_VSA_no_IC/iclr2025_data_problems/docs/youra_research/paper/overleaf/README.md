# Attribution Method Fingerprinting - Overleaf LaTeX Project

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Structure

- `main.tex` - Main document
- `references.bib` - BibTeX references
- `sections/` - Individual section files (00-08)
- `figures/` - Paper figures

## Requirements

- TeX Live 2025 or later
- ICML 2025 style files (icml2025.sty)
