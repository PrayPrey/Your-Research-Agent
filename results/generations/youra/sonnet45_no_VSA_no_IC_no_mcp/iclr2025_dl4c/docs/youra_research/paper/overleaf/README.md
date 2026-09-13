# ICML 2025 Overleaf Project

## Task-Dependent Feedback Orthogonality in Code Generation Alignment

This LaTeX project is ready for upload to Overleaf.

### Structure

```
overleaf/
├── main.tex                 # Main document
├── icml2025.sty            # ICML 2025 style file
├── icml2025.bst            # ICML 2025 bibliography style
├── references.bib          # BibTeX references
├── sections/               # Paper sections
│   ├── 01_abstract.tex
│   ├── 02_introduction.tex
│   ├── 03_related_work.tex
│   ├── 04_methodology.tex
│   ├── 05_experimental_setup.tex
│   ├── 06_results.tex
│   ├── 07_discussion.tex
│   └── 08_conclusion.tex
├── figures/                # Figures
│   ├── correlation_by_task.png
│   ├── correlation_heatmap.png
│   └── variance_decomposition.png
└── README.md               # This file
```

### Compilation

Local compilation:
```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

Or use the provided compile script:
```bash
cd overleaf
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

### Overleaf Upload

1. Create new Overleaf project (Blank Project)
2. Upload all files (drag entire folder or zip and upload)
3. Set main document to `main.tex`
4. Compile

### Note

ICML 2025 style files (icml2025.sty, icml2025.bst) are minimal working examples.
For submission, replace with official ICML 2025 style files from conference website.
