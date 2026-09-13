# Overleaf Project: Dose-Response Relationships in LLM Data Curation

## Quick Start

1. Upload this folder to Overleaf (zip and upload, or sync via GitHub)
2. Set `main.tex` as the main document
3. Compile with pdfLaTeX

## Structure

```
overleaf/
├── main.tex              # Main document
├── references.bib        # Bibliography
├── icml2025.sty          # ICML 2025 style file
├── sections/             # LaTeX sections
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related.tex
│   ├── methodology.tex
│   ├── experimental.tex
│   ├── results.tex
│   ├── discussion.tex
│   ├── conclusion.tex
│   └── appendix.tex
└── figures/              # All figures (PNG)
```

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Notes

- Uses booktabs for tables
- All figures referenced with `\includegraphics`
- Citations use natbib with plainnat style
