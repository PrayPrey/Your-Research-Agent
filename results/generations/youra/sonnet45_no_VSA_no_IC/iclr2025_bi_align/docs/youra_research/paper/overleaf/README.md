# Overleaf LaTeX Project - Contract-Based Validation Paper

## Compilation Instructions

### Standard Compilation (3-pass)

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Quick Check (single pass, no bibliography)

```bash
pdflatex main.tex
```

## Project Structure

```
overleaf/
├── main.tex                  # Main document
├── references.bib            # BibTeX references
├── sections/                 # LaTeX section files
│   ├── 01_abstract.tex
│   ├── 02_introduction.tex
│   ├── 03_related_work.tex
│   ├── 04_methodology.tex
│   ├── 05_experimental_setup.tex
│   ├── 06_results.tex
│   ├── 07_discussion.tex
│   └── 08_conclusion.tex
├── figures/                  # Figure assets (empty - no figures in source)
└── README.md                 # This file
```

## Output

Compiled PDF: `main.pdf`

## Notes

- Generated from Phase 6.5 final reviewed paper (06_paper_final.md)
- Uses standard article class (ICML style files not found in templates/)
- All special characters escaped for LaTeX (%, &, #, _, {, })
- Tables converted to booktabs format
- Citations converted from [Author, Year] to \cite{key} format
