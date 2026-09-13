# TC-SSM Paper - Overleaf LaTeX Project

## Structure

```
overleaf/
├── main.tex              # Main document
├── references.bib        # BibTeX references
├── sections/             # Paper sections
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_experimental_setup.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   ├── 07_conclusion.tex
│   └── 08_references.tex
└── figures/              # Paper figures (PNG)
```

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Overleaf Upload

1. Zip this folder
2. Upload to Overleaf as new project
3. Add ICML 2025 style files (icml2025.sty, icml2025.bst)
4. Compile

## Requirements

- ICML 2025 style files
- pdflatex with booktabs, amsmath, hyperref packages
