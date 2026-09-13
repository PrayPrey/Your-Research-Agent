# ICML 2025 Paper: Incremental SMT Verification for LLM Code Repair

## Overview

This Overleaf project contains the LaTeX source for the paper "Incremental SMT Verification for LLM Code Repair: Infrastructure Failure and Dataset Artifact Contribution".

**Status:** Camera-ready submission format (ICML 2025)

## Compilation Instructions

### Local Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The final PDF will be generated as `main.pdf`.

### Overleaf Upload

1. Create new Overleaf project
2. Upload all files from this directory:
   - `main.tex` (entry point)
   - `references.bib` (bibliography)
   - `sections/*.tex` (8 section files)
   - `figures/*.png` (3 figure files)
3. Set compiler to `pdfLaTeX`
4. Compile

## Structure

```
overleaf/
├── main.tex                    # Main document (includes sections, figures)
├── references.bib              # Bibliography entries
├── sections/
│   ├── 01_abstract.tex
│   ├── 02_introduction.tex
│   ├── 03_related_work.tex
│   ├── 04_methodology.tex
│   ├── 05_experimental_setup.tex
│   ├── 06_results.tex
│   ├── 07_discussion.tex
│   └── 08_conclusion.tex
└── figures/
    ├── gate_metrics.png
    ├── failure_modes.png
    └── success_by_complexity.png
```

## ICML 2025 Style

This paper uses the `icml2025` document class with `[accepted]` option for camera-ready submission. The style file is loaded via:

```latex
\usepackage[accepted]{icml2025}
```

**Note:** If compiling locally, ensure `icml2025.sty` is available in your LaTeX distribution or in the same directory as `main.tex`. Overleaf has this style file pre-installed.

## Key Features

- **9 LaTeX sections:** Abstract through Conclusion + Appendix
- **3 figures:** Gate metrics, failure modes, complexity analysis (see Appendix)
- **12 BibTeX references:** Angelix, Prophet, Z3, Pyre, Prusti, AlphaCode, CodeT5, CURE, CoCoNut, HumanEval, Pydantic
- **Modular structure:** Each section in separate `.tex` file for easy editing

## Author Information

**Current:** Anonymous submission format

**Before final submission:** Update author block in `main.tex` lines 19-23 with actual names, affiliations, emails.

## Compilation Requirements

- pdfLaTeX compiler
- BibTeX for bibliography
- Standard LaTeX packages: `booktabs`, `amsmath`, `graphicx`, `hyperref`
- ICML 2025 style file (`icml2025.sty`)

## Troubleshooting

**Problem:** `icml2025.sty not found`
**Solution:** Download from ICML 2025 author kit or use Overleaf (pre-installed).

**Problem:** Figures not displaying
**Solution:** Ensure `figures/` folder contains `.png` files in same directory as `main.tex`.

**Problem:** Bibliography empty
**Solution:** Run `bibtex main` after first `pdflatex` pass, then recompile twice.

## Contact

For questions about this submission, contact [anonymous during review].
