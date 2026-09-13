# Overleaf LaTeX Project - Benchmark Saturation Detection

Generated from Phase 6.5.1 workflow on 2026-08-28.

## Structure

```
overleaf/
├── main.tex                 # Main document
├── references.bib           # BibTeX references
├── sections/                # Paper sections
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_experimental_setup.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   └── 07_conclusion.tex
└── figures/                 # All figures
    ├── agreement_bars.png
    ├── confidence_stratification.png
    ├── convergence_timeline_imagenet.png
    ├── gate_metrics.png
    ├── lead_time_histogram.png
    └── timeline.png
```

## Compilation

### Local Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Overleaf Upload

1. Zip the entire `overleaf/` directory
2. Upload to Overleaf as new project
3. Set compiler to `pdfLaTeX`
4. Compile

### Output

Compiled PDF: `main.pdf`

## Notes

- Converted from Markdown (06_paper_final.md)
- All citations updated to \cite{} format
- Tables use booktabs format
- Figures use standard LaTeX figure environments
- Special characters properly escaped (%, &, #, _, {, })

## ICML 2025 Style

To use ICML 2025 style files:
1. Download style files from ICML website
2. Replace `\documentclass{article}` with `\documentclass{icml2025}`
3. Update preamble as per ICML template
