# Overleaf LaTeX Project: Gradient Abnormality for Spurious Correlation Detection

## Structure

```
overleaf/
├── main.tex                    # Main document
├── icml2025.sty                # ICML 2025 style file (fallback)
├── references.bib              # Bibliography (copied from 06_references.bib)
├── sections/                   # Section files
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_methodology.tex
│   ├── 04_experiments.tex
│   ├── 05_results.tex
│   ├── 06_discussion.tex
│   └── 07_conclusion.tex
└── figures/                    # Figure directory (empty, no figures in original paper)
```

## Compilation

Compile with standard LaTeX workflow:

```bash
cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scsl/docs/youra_research/paper/overleaf
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf`

## Dependencies

- LaTeX distribution (TeX Live, MiKTeX, etc.)
- Required packages: times, graphicx, amsmath, amssymb, natbib, algorithm, algorithmic, booktabs, hyperref

## Notes

- Original paper source: `../06_paper_final.md`
- Bibliography converted from Markdown citations to BibTeX
- Style file: ICML 2025 fallback (minimal implementation)
- Figures: Not included (original paper has no embedded figures)
- Tables: Converted to booktabs format in LaTeX

## Upload to Overleaf

1. Create new Overleaf project
2. Upload all files maintaining directory structure
3. Set main document to `main.tex`
4. Compile
