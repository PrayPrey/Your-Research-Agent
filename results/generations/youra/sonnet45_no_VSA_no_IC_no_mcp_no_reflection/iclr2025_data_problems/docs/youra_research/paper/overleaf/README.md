# ICML 2025 Paper - Overleaf Project

**Title:** Data Quality as Compute Efficiency Multiplier: Quantifying the Information Density of Foundation Model Pretraining Corpora

## Directory Structure

```
overleaf/
├── main.tex                    # Main LaTeX document
├── icml2025.sty               # ICML 2025 style file (fallback)
├── icml2025.bst               # BibTeX style
├── references.bib             # Bibliography
├── sections/                  # Paper sections (9 .tex files)
│   ├── 01_abstract.tex
│   ├── 02_introduction.tex
│   ├── 03_related_work.tex
│   ├── 04_methodology.tex
│   ├── 05_experimental_setup.tex
│   ├── 06_results.tex
│   ├── 07_discussion.tex
│   ├── 08_conclusion.tex
│   └── 09_acknowledgments.tex
└── figures/                   # Figures (2 PNG files)
    ├── fig_quality_comparison.png
    └── fig_mechanism_validation.png
```

## Build Instructions

### Local Compilation

```bash
cd overleaf/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf`

### Overleaf Upload

1. Create new project on Overleaf
2. Upload all files maintaining directory structure
3. Set compiler to pdfLaTeX
4. Compile

## Files Generated

- **9 section .tex files** (120KB total): Converted from 06_paper_final.md
- **main.tex** (2.5KB): LaTeX document structure
- **references.bib** (7.6KB): 28 citations
- **2 figures** (230KB total): PNG visualizations
- **Style files** (icml2025.sty, icml2025.bst): Fallback ICML formatting

## Notes

- ICML 2025 official style unavailable; fallback article-based style used
- All LaTeX special characters escaped (%, $, _, &, #)
- Tables use booktabs formatting
- Figures referenced as fig:composite, fig:importance
- Anonymous submission format (author/institution placeholders)

## Conversion Details

- Source: `paper/06_paper_final.md` (52KB, 648 lines)
- Target: 9 modular .tex sections
- Math equations: Converted to LaTeX equation environments
- Citations: Converted to \cite{} format
- Tables: Converted to booktabs tabular format
- Special chars: Properly escaped (e.g., % -> \%, $ -> \$)

Generated: 2026-08-28 (Phase 6.5.1 - Overleaf Conversion)
