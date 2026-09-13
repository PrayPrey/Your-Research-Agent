# Scale-Dependent Error Patterns in LLM Code Judges

Overleaf-ready LaTeX project generated from 06_paper_final.md.

## Structure

```
overleaf/
├── main.tex           # Main document
├── icml2025.sty       # ICML 2025 style
├── references.bib     # Bibliography
├── sections/          # Section files
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related.tex
│   ├── 03_methodology.tex
│   ├── 04_setup.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   └── 07_conclusion.tex
└── figures/           # PNG figures
```

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Upload to Overleaf

1. Zip the entire `overleaf/` folder
2. Upload to Overleaf as new project
3. Set main document to `main.tex`
