# Overleaf LaTeX Project

**Paper:** Symmetry Orbits Are Geometrically Large in MLP Weight Spaces: Implications for Weight Space Encoding  
**Format:** ICML 2025  
**Generated:** 2026-08-27 by Anonymous Research Pipeline — Phase 6.5.1

---

## Quick Start (Overleaf)

1. Upload this entire `overleaf/` folder to a new Overleaf project
2. Set `main.tex` as the main document
3. Set compiler to **pdfLaTeX**
4. Compile: BibTeX → pdfLaTeX → pdfLaTeX

---

## Local Compilation

```bash
cd paper/overleaf/
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
cp main.pdf output.pdf
```

---

## Checklist Before Submission

- [ ] Replace `Anonymous Author` with real author names
- [ ] Replace `Anonymous Institution` with real affiliation
- [ ] Replace `anonymous@anonymous.org` with real email
- [ ] Add acknowledgements section
- [ ] Verify all `\cite{}` keys match entries in `references.bib`
- [ ] Verify all `\includegraphics{}` figure files exist
- [ ] Review `icml2025` formatting requirements at icml.cc

---

## Project Structure

```
overleaf/
├── main.tex                    # Main document
├── references.bib              # BibTeX bibliography
├── icml2025.sty               # ICML 2025 style file
├── icml2025.bst               # ICML 2025 bibliography style
├── algorithm.sty              # Algorithm environment
├── algorithmic.sty            # Algorithmic environment
├── fancyhdr.sty               # Header/footer package
├── sections/
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── methodology.tex
│   ├── experiments.tex
│   ├── results.tex
│   ├── discussion.tex
│   ├── conclusion.tex
│   └── appendix.tex
└── figures/                    # 23 figure files
```

---

## Human Action Required

1. **Author information:** Replace placeholders in `main.tex` (`icmlauthorlist`, `icmlaffiliation`, `icmlcorrespondingauthor`)
2. **Acknowledgements:** Uncomment and fill the acknowledgements section in `main.tex`
3. **Review notes:** See `065_human_review_notes.md` (in parent folder) for minor fixes from adversarial review
4. **Final quality check:** Compile in Overleaf and verify formatting, figure placement, and reference correctness
