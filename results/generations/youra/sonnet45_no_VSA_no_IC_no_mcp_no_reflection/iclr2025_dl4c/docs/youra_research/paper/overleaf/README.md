# Overleaf Project: Fix-Impact-Ratio Paper

Generated from `06_paper_final.md` using Phase 6.5.1 Markdown-to-LaTeX conversion pipeline.

## Directory Structure

```
overleaf/
├── main.tex                    # Main document file
├── references.bib              # BibTeX bibliography
├── sections/                   # LaTeX section files
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── methodology.tex
│   ├── experimental_setup.tex
│   ├── results.tex
│   ├── discussion.tex
│   └── conclusion.tex
└── figures/                    # PNG figures
    ├── cluster_vs_impact.png
    ├── cumulative_tests.png
    ├── fix_impact_distribution.png
    └── proportion_comparison.png
```

## Compilation Instructions

### Local Compilation (pdflatex + bibtex)

```bash
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_dl4c/docs/youra_research/paper/overleaf

# First pass: generate .aux file
pdflatex main.tex

# Process bibliography
bibtex main

# Second pass: resolve citations
pdflatex main.tex

# Third pass: resolve cross-references
pdflatex main.tex
```

Output: `main.pdf`

### Overleaf Upload

1. Create new project on Overleaf (https://www.overleaf.com)
2. Upload all files maintaining directory structure:
   - Upload `main.tex`, `references.bib`, `README.md` to root
   - Create `sections/` folder and upload 8 .tex files
   - Create `figures/` folder and upload 4 .png files
3. Set main document to `main.tex`
4. Compile (Overleaf handles pdflatex + bibtex automatically)

## Conversion Notes

- **Special Characters Escaped:** `~` → `\textasciitilde`, `%` → `\%`, `_` → `\_`, `#` → `\#`
- **Citations:** Markdown `~\cite{key}` → LaTeX `\cite{key}` (tilde kept for spacing)
- **Math Inline:** `$...$` preserved
- **Math Display:** `$$...$$` → `\begin{equation}...\end{equation}`
- **Tables:** Markdown → `booktabs` format (`\toprule`, `\midrule`, `\bottomrule`)
- **Figures:** PNG files referenced with `\includegraphics[width=0.8\columnwidth]{figures/filename.png}`
- **Emphasis:** `*text*` → `\emph{text}`, `**bold**` → `\textbf{bold}`
- **Code:** `` `code` `` → `\texttt{code}`
- **Arrows:** `→` → `\rightarrow`

## Validation Checklist

- [x] 9 section files created (abstract through conclusion)
- [x] 4 figures copied (cluster_vs_impact, cumulative_tests, fix_impact_distribution, proportion_comparison)
- [x] references.bib copied
- [x] main.tex generated with correct \input{} structure
- [ ] Compilation successful (run pdflatex + bibtex)
- [ ] Output PDF exists and is non-empty

## Paper Metadata

- **Title:** Fix-Impact-Ratio: Measuring Strategic Debugging in Code Generation Agents
- **Sections:** 8 (Abstract, Introduction, Related Work, Methodology, Experimental Setup, Results, Discussion, Conclusion)
- **Figures:** 4 PNG images
- **Tables:** 4 (embedded in results.tex)
- **Citations:** 10 references in references.bib
- **Target Conference:** ICML 2025 (placeholder; adjust documentclass/style as needed)

## Known Issues / Future Adjustments

- Author information anonymized (`Anonymous Author(s)`) — replace before submission
- No ICML-specific style file included — using generic `article` documentclass
- Figure placement uses `[h]` (here) — may need adjustment for final layout
- No appendix section (none in original markdown)
- Tables not labeled with \ref{} cross-references in text — add if needed
