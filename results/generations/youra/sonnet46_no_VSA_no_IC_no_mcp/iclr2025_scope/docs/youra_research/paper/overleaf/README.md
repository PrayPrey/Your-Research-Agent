# Overleaf LaTeX Project

Paper: "The Cache Format Matters: A Reproducible Baseline and Implementation Protocol for KV Cache Eviction in Modern Transformer Libraries"

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Structure

- `main.tex` — root document
- `sections/` — 9 .tex section files (00_abstract through 08_acknowledgments)
- `references.bib` — BibTeX references
- `figures/` — paper figures
- `icml2025.sty` — ICML 2025 style file
- `icml2025.bst` — ICML 2025 bibliography style

## Notes

- Target venue: ICML 2025
- All citations marked "(to be verified before submission)"
- Anonymous double-blind submission format
