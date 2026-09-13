# ProvenanceCache - ICML 2025 Overleaf Project

Generated from Phase 6.5.1: Overleaf LaTeX + PDF Pipeline

## Quick Start (Overleaf)

1. **Upload to Overleaf**:
   - Create new blank Overleaf project
   - Upload all files from this folder (including subdirectories)

2. **Compiler Settings**:
   - Compiler: **pdfLaTeX**
   - Main document: **main.tex**

3. **Compilation**:
   - Click "Recompile" (Overleaf handles bibtex automatically)
   - First compile may take 30-60 seconds

## Local Compilation

```bash
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Output: `main.pdf`

## Project Structure

```
overleaf/
├── main.tex              # Root document
├── references.bib        # Bibliography
├── sections/             # Paper sections (9 files)
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── methodology.tex
│   ├── experiments.tex
│   ├── results.tex
│   ├── discussion.tex
│   └── conclusion.tex
├── figures/              # Figures (if any)
├── icml2025.sty          # ICML style file
├── icml2025.bst          # ICML bibliography style
└── README.md             # This file
```

## Before Submission Checklist

- [ ] Replace author placeholders with real names/affiliations
- [ ] Add acknowledgements section
- [ ] Verify all citations resolve (no "?" in PDF)
- [ ] Check figure references (if figures added)
- [ ] Run spell check
- [ ] Verify page limit compliance (ICML 2025: 8 pages + unlimited references)
- [ ] Review 065_human_review_notes.md for minor fixes flagged during adversarial review

## ICML 2025 Style Files

Official style files included:
- `icml2025.sty` - Main style package
- `icml2025.bst` - Bibliography style

If missing, download from: https://media.icml.cc/Conferences/ICML2025/Styles/icml2025.zip

## Notes

- **Generated**: 2026-08-21 (automated conversion from Markdown)
- **Phase**: 6.5.1 (Overleaf + PDF Generation)
- **Mock Data**: F1 scores from mock validation (real GPU validation pending)

For questions, refer to Phase 6.5.1 workflow documentation.
