# Overleaf LaTeX Project: Formal Deprecation Mechanisms for ML Dataset Repositories

Auto-generated LaTeX project from Phase 6.5.1 Overleaf Export.

## Project Structure

```
overleaf/
├── main.tex                 # Main document (compile this)
├── references.bib           # BibTeX bibliography
├── sections/               # LaTeX section files
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── methodology.tex
│   ├── experimental_setup.tex
│   ├── results.tex
│   ├── discussion.tex
│   └── conclusion.tex
└── figures/                # PNG figures
    ├── h-e1_*.png          (4 files)
    └── h-m1_*.png          (5 files)
```

## Build Instructions

### Local Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf`

### Overleaf Upload

1. Create new Overleaf project (blank template)
2. Upload all files maintaining folder structure
3. Set main document: `main.tex`
4. Compile (Overleaf auto-detects pdflatex + bibtex)

## Source Document

Generated from: `paper/06_paper_final.md` (29110 bytes)
Bibliography: `paper/06_references.bib` (1524 bytes)
Figures: `paper/figures/` (9 PNG files, 296K total)

## Notes

- ICML 2025 format (modify `\documentclass` for venue-specific style files)
- Anonymous submission template (author placeholders in `main.tex`)
- References use `plain` style; adjust `\bibliographystyle{}` as needed
- Figures referenced by filename; embed via `\includegraphics{}` in section .tex files
