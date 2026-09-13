# Overleaf LaTeX Project: Attention-Based Failure Routing

Generated from Phase 6.5.1 Overleaf Export Workflow

## Contents

- `main.tex` - Main document (includes all sections)
- `sections/` - Individual section files (01_abstract.tex through 08_conclusion.tex)
- `figures/` - All figures (12 PNG files)
- `references.bib` - Bibliography (8 citations)
- `icml2025.sty` - ICML 2025 style package (minimal placeholder)

## Compilation

Standard LaTeX compilation sequence:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf`

## Upload to Overleaf

1. Create new blank project on Overleaf
2. Upload all files preserving directory structure:
   - Root: main.tex, references.bib, icml2025.sty
   - sections/ folder: 01_abstract.tex through 08_conclusion.tex
   - figures/ folder: all PNG files
3. Set main document: main.tex
4. Compile

## Notes

- ICML 2025 style file is a minimal placeholder. For actual submission, download official style from https://icml.cc/Conferences/2025/StyleAuthorInstructions
- All figures referenced via \includegraphics are PNG format (12 figures total)
- BibTeX references use `natbib` package with `plainnat` style
- Document structure: 8 sections + 3 inline figures + bibliography
