# Phase 6.5.1: Overleaf LaTeX + PDF Generation - Validation Checklist

## Step 1: Initialize

- [ ] `paper/06_paper_final.md` exists (FATAL if missing)
- [ ] `paper/overleaf/` folder created
- [ ] `paper/overleaf/sections/` subfolder created
- [ ] `paper/overleaf/figures/` subfolder created
- [ ] `pdflatex` availability checked
- [ ] `bibtex` availability checked
- [ ] ICML 2025 style files checked (`icml2025.sty`, `icml2025.bst`)

## Step 2: Markdown to LaTeX Conversion

### Section Parsing
- [ ] `06_paper_final.md` split into sections
- [ ] All expected sections identified (abstract through conclusion)

### Conversion Quality
- [ ] `sections/abstract.tex` generated
- [ ] `sections/introduction.tex` generated
- [ ] `sections/related_work.tex` generated
- [ ] `sections/methodology.tex` generated
- [ ] `sections/experiments.tex` generated
- [ ] `sections/results.tex` generated
- [ ] `sections/discussion.tex` generated
- [ ] `sections/conclusion.tex` generated
- [ ] `sections/appendix.tex` generated (if appendix exists in source)

### Conversion Rules Applied
- [ ] `#/##/###` headers → `\section{}/\subsection{}/\subsubsection{}`
- [ ] `**bold**` → `\textbf{}`
- [ ] `*italic*` → `\textit{}`
- [ ] Special characters escaped (`%`, `&`, `#`, `_`, `{`, `}`)
- [ ] Markdown tables → `\begin{table}` with `booktabs`
- [ ] `![Figure N: caption](figures/filename.png)` → `\begin{figure}...\includegraphics{}`
- [ ] `[Author, Year]` citations → `\cite{key}` or `\citep{key}`
- [ ] Inline math `$...$` preserved
- [ ] Display math `$$...$$` → `\begin{equation}...\end{equation}`
- [ ] Abstract uses `\begin{abstract}` (no `\section{}`)

## Step 3: Assemble Project

- [ ] `main.tex` generated from template
- [ ] `{PAPER_TITLE}` placeholder replaced with actual title
- [ ] `{PAPER_TITLE_SHORT}` placeholder replaced
- [ ] No placeholder tokens remaining in `main.tex`
- [ ] `references.bib` copied from `paper/06_references.bib`
- [ ] All figures copied from `paper/figures/` to `overleaf/figures/`
- [ ] `README.md` generated with compilation instructions

## Step 4: Compile and Verify

### Compilation
- [ ] `pdflatex main.tex` (first pass) executed
- [ ] `bibtex main` executed
- [ ] `pdflatex main.tex` (second pass) executed
- [ ] `pdflatex main.tex` (third pass) executed
- [ ] `output.pdf` created (copied from `main.pdf`)

### Verification
- [ ] `output.pdf` exists and is > 0 bytes
- [ ] All 8-9 section `.tex` files exist in `sections/`
- [ ] `main.tex` has no placeholder tokens
- [ ] `references.bib` exists
- [ ] All `\includegraphics{}` files exist in `figures/` (warning if not)
- [ ] All `\cite{}` keys exist in `.bib` (warning if not)

### Pipeline State
- [ ] `verification_state.yaml` updated with `overleaf_generation` section
- [ ] `.phase_state.json` created via `create_phase_state.py`
- [ ] `.phase_state.json` has `next_action.type: "stop"` (final phase)

---

## Output Verification

| Output | Path | Verified |
|--------|------|----------|
| `main.tex` | `paper/overleaf/main.tex` | [ ] |
| `references.bib` | `paper/overleaf/references.bib` | [ ] |
| Section .tex files | `paper/overleaf/sections/*.tex` | [ ] |
| Figures | `paper/overleaf/figures/*` | [ ] |
| Compiled PDF | `paper/overleaf/output.pdf` | [ ] |
| README | `paper/overleaf/README.md` | [ ] |

---

## Figure Pipeline Verification

- [ ] `paper/figures/` scanned for source figures
- [ ] All source figures copied to `overleaf/figures/`
- [ ] `![Figure N: caption](figures/filename.png)` patterns in MD converted to `\includegraphics{}`
- [ ] Each `\begin{figure}` has `\caption{}` and `\label{}`
- [ ] Figure filenames in `\includegraphics{}` match actual files in `overleaf/figures/`

---

## Error Handling

- [ ] Missing style file: warned and continued
- [ ] Compilation failure: log analyzed, fix attempted (max 3 retries)
- [ ] Missing figures: warned and continued with placeholders
- [ ] Missing citations: warned (removed `\cite{}` or added to `.bib`)

---

## Validation Summary

**Total Checks:** 55+
**Required:** Step 1 (inputs) + Step 2 (conversion) + Step 3 (assembly) + Step 4 (state)

**Minimum Pass Criteria:**
- `06_paper_final.md` read successfully
- At least 7 section `.tex` files generated
- `main.tex` generated with no placeholder tokens
- Figures copied to `overleaf/figures/`
- PDF compilation attempted (success or documented partial)
- `.phase_state.json` created with correct phase name
- `verification_state.yaml` updated

**Compilation is desirable but NOT required for PASS:**
- If `pdflatex` fails after 3 retries → PASS with `compilation_status: "PARTIAL"`
- LaTeX project itself is the primary deliverable

---

**Validation Result:**
- ✅ SUCCESS: LaTeX project created, PDF compiled
- ⚠️ PARTIAL: LaTeX project created, PDF compilation failed (documented)
- ❌ FAILURE: LaTeX project not created or pipeline state not updated

**Validator:** Phase 6.5.1 Overleaf Workflow (YouRA)
