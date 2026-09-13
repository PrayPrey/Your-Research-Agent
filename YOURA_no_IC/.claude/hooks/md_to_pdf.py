#!/usr/bin/env python3
"""
md_to_pdf.py — Convert a Markdown paper to LaTeX (ICML 2025 format) and compile to PDF.

Standalone script that:
  1. Parses a Markdown paper into sections
  2. Converts each section to LaTeX
  3. Generates main.tex with ICML 2025 template
  4. Copies figures and references if available
  5. Compiles with pdflatex + bibtex (3 passes)

Usage:
  python md_to_pdf.py --input paper.md --output-dir output_latex/
  python md_to_pdf.py --input paper.md --output-dir output_latex/ --figures-dir figures/ --bib refs.bib

Author: Anonymous
Version: 1.0
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# ============================================================
# Markdown to LaTeX conversion
# ============================================================

def convert_markdown_to_latex(md_text):
    """Convert markdown formatting to LaTeX."""
    lines = md_text.split('\n')
    latex_lines = []
    in_list = False
    in_enumerate = False
    in_table = False
    in_code_block = False
    table_rows = []

    for line in lines:
        # Fenced code block toggle (``` or ~~~). Emit verbatim, do not process
        # markdown/math/citations inside.
        if line.lstrip().startswith('```') or line.lstrip().startswith('~~~'):
            if in_code_block:
                latex_lines.append(r'\end{verbatim}')
                in_code_block = False
            else:
                # close any other open block before opening verbatim
                if in_list:
                    latex_lines.append(r'\end{itemize}'); in_list = False
                if in_enumerate:
                    latex_lines.append(r'\end{enumerate}'); in_enumerate = False
                if in_table:
                    _flush_table(latex_lines, table_rows); in_table = False; table_rows = []
                latex_lines.append(r'\begin{verbatim}')
                in_code_block = True
            continue
        if in_code_block:
            latex_lines.append(line)
            continue

        # Skip YAML frontmatter and horizontal rules
        if line.strip() in ['---']:
            continue

        # Empty line
        if not line.strip():
            if in_list:
                latex_lines.append(r'\end{itemize}')
                in_list = False
            if in_enumerate:
                latex_lines.append(r'\end{enumerate}')
                in_enumerate = False
            if in_table:
                _flush_table(latex_lines, table_rows)
                in_table = False
                table_rows = []
            latex_lines.append('')
            continue

        # Table detection
        if '|' in line and line.strip().startswith('|'):
            # Skip separator rows (|---|---|)
            if re.match(r'^\|[\s\-:| ]+\|$', line.strip()):
                continue
            in_table = True
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            table_rows.append(cells)
            continue
        elif in_table:
            _flush_table(latex_lines, table_rows)
            in_table = False
            table_rows = []

        # Headers
        if line.startswith('### '):
            _close_lists(latex_lines, in_list, in_enumerate)
            in_list = in_enumerate = False
            title = line[4:].strip()
            latex_lines.append(f'\\subsubsection{{{_escape_latex_text(title)}}}')
            continue
        elif line.startswith('## '):
            _close_lists(latex_lines, in_list, in_enumerate)
            in_list = in_enumerate = False
            title = line[3:].strip()
            # Remove numbering like "1. Introduction" -> "Introduction"
            title = re.sub(r'^\d+\.\s*', '', title)
            latex_lines.append(f'\\subsection{{{_escape_latex_text(title)}}}')
            continue
        elif line.startswith('# '):
            continue  # Top-level headers handled by section splitting

        # Lists
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                latex_lines.append(r'\begin{itemize}')
                in_list = True
            item = line.strip()[2:]
            latex_lines.append(f'\\item {_convert_inline(item)}')
            continue
        elif re.match(r'^\s*\d+\.\s', line):
            if not in_enumerate:
                latex_lines.append(r'\begin{enumerate}')
                in_enumerate = True
            item = re.sub(r'^\s*\d+\.\s', '', line)
            latex_lines.append(f'\\item {_convert_inline(item)}')
            continue
        else:
            if in_list:
                latex_lines.append(r'\end{itemize}')
                in_list = False
            if in_enumerate:
                latex_lines.append(r'\end{enumerate}')
                in_enumerate = False

        # Figure references: ![alt](path)
        fig_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)', line.strip())
        if fig_match:
            alt_text = fig_match.group(1)
            fig_path = fig_match.group(2)
            fig_basename = os.path.basename(fig_path)
            fig_name = os.path.splitext(fig_basename)[0]
            caption = alt_text if alt_text else fig_name.replace('_', ' ').title()
            latex_lines.append(r'\begin{figure}[htbp]')
            latex_lines.append(r'\centering')
            latex_lines.append(f'\\includegraphics[width=\\columnwidth]{{figures/{fig_basename}}}')
            latex_lines.append(f'\\caption{{{_escape_latex_text(caption)}}}')
            latex_lines.append(f'\\label{{fig:{fig_name}}}')
            latex_lines.append(r'\end{figure}')
            continue

        # Regular text
        latex_lines.append(_convert_inline(line))

    # Close any open environments
    if in_list:
        latex_lines.append(r'\end{itemize}')
    if in_enumerate:
        latex_lines.append(r'\end{enumerate}')
    if in_table:
        _flush_table(latex_lines, table_rows)

    return '\n'.join(latex_lines)


def _close_lists(latex_lines, in_list, in_enumerate):
    if in_list:
        latex_lines.append(r'\end{itemize}')
    if in_enumerate:
        latex_lines.append(r'\end{enumerate}')


def _flush_table(latex_lines, table_rows):
    """Convert accumulated table rows to a booktabs table that fits the
    ICML two-column layout:
      - <=4 columns: single-column `table` with `l` cols
      - >=5 columns: two-column-spanning `table*`, columns sized by the
        longest cell in each column, with `\\resizebox` as a safety net
        so the tabular never overflows \\textwidth.
    """
    if not table_rows:
        return
    n_cols = max(len(r) for r in table_rows)
    wide = n_cols >= 5

    # Pad rows and compute per-column max cell length (after escaping) for
    # rough column-width hints.
    padded = []
    for row in table_rows:
        row = list(row) + [''] * (n_cols - len(row))
        padded.append([_escape_latex_text(c) for c in row])

    col_spec = 'l' * n_cols
    env = 'table*' if wide else 'table'
    if wide:
        box_w = r'\dimexpr 2\columnwidth+\columnsep\relax'
    else:
        box_w = r'\columnwidth'

    latex_lines.append(f'\\begin{{{env}}}[htbp]')
    latex_lines.append(r'\centering')
    # Always scale-to-fit so the tabular never exceeds the available width,
    # regardless of how long individual cells are.
    latex_lines.append(f'\\resizebox{{{box_w}}}{{!}}{{%')
    latex_lines.append(f'\\begin{{tabular}}{{{col_spec}}}')
    latex_lines.append(r'\toprule')

    for i, row in enumerate(padded):
        latex_lines.append(' & '.join(row) + r' \\')
        if i == 0:
            latex_lines.append(r'\midrule')

    latex_lines.append(r'\bottomrule')
    latex_lines.append(r'\end{tabular}')
    latex_lines.append(r'}')
    latex_lines.append(f'\\end{{{env}}}')


UNICODE_TO_LATEX = {
    'α': r'$\alpha$', 'β': r'$\beta$', 'γ': r'$\gamma$', 'δ': r'$\delta$',
    'ε': r'$\epsilon$', 'ζ': r'$\zeta$', 'η': r'$\eta$', 'θ': r'$\theta$',
    'ι': r'$\iota$', 'κ': r'$\kappa$', 'λ': r'$\lambda$', 'μ': r'$\mu$',
    'ν': r'$\nu$', 'ξ': r'$\xi$', 'π': r'$\pi$', 'ρ': r'$\rho$',
    'σ': r'$\sigma$', 'τ': r'$\tau$', 'υ': r'$\upsilon$', 'φ': r'$\phi$',
    'χ': r'$\chi$', 'ψ': r'$\psi$', 'ω': r'$\omega$',
    'Α': r'A', 'Β': r'B', 'Γ': r'$\Gamma$', 'Δ': r'$\Delta$',
    'Θ': r'$\Theta$', 'Λ': r'$\Lambda$', 'Ξ': r'$\Xi$', 'Π': r'$\Pi$',
    'Σ': r'$\Sigma$', 'Φ': r'$\Phi$', 'Ψ': r'$\Psi$', 'Ω': r'$\Omega$',
    '±': r'$\pm$', '×': r'$\times$', '÷': r'$\div$', '≤': r'$\leq$',
    '≥': r'$\geq$', '≠': r'$\neq$', '≈': r'$\approx$', '∞': r'$\infty$',
    '→': r'$\rightarrow$', '←': r'$\leftarrow$', '↔': r'$\leftrightarrow$',
    '∈': r'$\in$', '∉': r'$\notin$', '⊂': r'$\subset$', '⊃': r'$\supset$',
    '∪': r'$\cup$', '∩': r'$\cap$', '∅': r'$\emptyset$',
    '∑': r'$\sum$', '∏': r'$\prod$', '∫': r'$\int$',
    '√': r'$\sqrt{}$', '∂': r'$\partial$', '∇': r'$\nabla$',
    '⟨': r'$\langle$', '⟩': r'$\rangle$',
    '–': r'--', '—': r'---', ''': r"`", ''': r"'", '"': r'``', '"': r"''",
    '…': r'\ldots{}',
    # --- additions for math glyphs that appeared in rewrites ---
    'ℓ': r'$\ell$', 'ℝ': r'$\mathbb{R}$', '⊗': r'$\otimes$',
    '‖': r'$\|$', '·': r'$\cdot$', '−': r'-',
    # subscripts
    'ᵢ': r'$_i$', '₀': r'$_0$', '₁': r'$_1$', '₂': r'$_2$',
    '₃': r'$_3$', '₄': r'$_4$', '₅': r'$_5$', '₆': r'$_6$',
    '₇': r'$_7$', '₈': r'$_8$', '₉': r'$_9$',
    # superscripts
    '⁰': r'$^0$', '¹': r'$^1$', '²': r'$^2$', '³': r'$^3$', '⁴': r'$^4$',
    '⁵': r'$^5$', '⁶': r'$^6$', '⁷': r'$^7$', '⁸': r'$^8$', '⁹': r'$^9$',
    '⁻': r'$^-$', '⁺': r'$^+$',
}


_COMBINING_TILDE = '̃'

# Map a math-glyph (when seen inside a math run) to its raw LaTeX form
# (no surrounding $). When the glyph appears OUTSIDE a math run, the
# fallback UNICODE_TO_LATEX table wraps it in $...$ on its own.
_MATH_GLYPH = {
    '‖': r'\|', '∇': r'\nabla ', 'ℓ': r'\ell ', '⊗': r'\otimes ',
    '·': r'\cdot ', '−': '-', 'ℝ': r'\mathbb{R}',
    '≤': r'\leq ', '≥': r'\geq ', '≈': r'\approx ', '≠': r'\neq ',
    '±': r'\pm ', '×': r'\times ', '÷': r'\div ',
    '∈': r'\in ', '∉': r'\notin ', '⊂': r'\subset ', '⊃': r'\supset ',
    '∪': r'\cup ', '∩': r'\cap ', '∅': r'\emptyset ',
    '∑': r'\sum ', '∏': r'\prod ', '∫': r'\int ',
    '∂': r'\partial ', '∞': r'\infty ', '√': r'\sqrt',
    '→': r'\rightarrow ', '←': r'\leftarrow ', '↔': r'\leftrightarrow ',
    '⟨': r'\langle ', '⟩': r'\rangle ',
    'α': r'\alpha ', 'β': r'\beta ', 'γ': r'\gamma ', 'δ': r'\delta ',
    'ε': r'\epsilon ', 'θ': r'\theta ', 'λ': r'\lambda ', 'μ': r'\mu ',
    'π': r'\pi ', 'σ': r'\sigma ', 'τ': r'\tau ', 'φ': r'\phi ',
    'ψ': r'\psi ', 'ω': r'\omega ', 'Δ': r'\Delta ', 'Σ': r'\Sigma ',
    'ᵢ': '_i',
    '₀': '_0', '₁': '_1', '₂': '_2', '₃': '_3', '₄': '_4',
    '₅': '_5', '₆': '_6', '₇': '_7', '₈': '_8', '₉': '_9',
    '⁰': '^0', '¹': '^1', '²': '^2', '³': '^3', '⁴': '^4',
    '⁵': '^5', '⁶': '^6', '⁷': '^7', '⁸': '^8', '⁹': '^9',
    '⁻': '^-', '⁺': '^+',
}

# Characters that count as "inside a math run" when they sit between or
# next to math glyphs: ASCII letters/digits, operators, parens, braces,
# backslash, single underscore/caret, whitespace.
_MATH_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    "+-/=,()[]{}|^_."
)
# Inside a math run we tolerate a single space, but two consecutive spaces
# (or any other non-math char) terminate the run.
_MATH_GLYPH_CHARS = set(_MATH_GLYPH.keys())


def _is_glyph(ch: str) -> bool:
    return ch in _MATH_GLYPH_CHARS


def _convert_math_run(run: str) -> str:
    """Translate a detected math-run substring into LaTeX (no surrounding $)."""
    out = []
    i = 0
    while i < len(run):
        ch = run[i]
        if ch == _COMBINING_TILDE:
            i += 1
            continue
        nxt = run[i + 1] if i + 1 < len(run) else ''
        if nxt == _COMBINING_TILDE and ch.isalpha():
            out.append(r'\tilde{' + ch + '}')
            i += 2
            continue
        if ch in _MATH_GLYPH:
            out.append(_MATH_GLYPH[ch])
            i += 1
            continue
        out.append(ch)
        i += 1
    result = ''.join(out)
    # Combine sequential single-char super/subscripts emitted from
    # unicode super/sub digits (e.g. ⁻¹³ -> ^-^1^3 -> ^{-13}).
    def _combine_seq(text, prefix):
        pat = re.compile(rf"((?:\{prefix}[\-+0-9])(?:\{prefix}[\-+0-9])+)")
        def repl(m):
            s = m.group(1)
            chars = ''.join(s[i + 1] for i in range(0, len(s), 2))
            return f"{prefix}{{{chars}}}"
        return pat.sub(repl, text)
    result = _combine_seq(result, '^')
    result = _combine_seq(result, '_')
    # Inside a single math expression, X_a_b causes "double subscript".
    # Convert the second-and-later `_` in identifier-like runs to \_.
    def _fix_double_sub(m):
        return m.group(1) + '\\' + m.group(2)
    result = re.sub(r"([A-Za-z]_[A-Za-z0-9]+)(_[A-Za-z0-9]+)", _fix_double_sub, result)
    # Wrap single-character subscripts/superscripts in braces so that a
    # following `_{..}` or `^{..}` attached to the surrounding group is
    # unambiguous. e.g. {\tilde{g}_i}_{i=1}^N -> {\tilde{g}_{i}}_{i=1}^N
    result = re.sub(r"_([A-Za-z0-9])(?=[^A-Za-z0-9{])", r"_{\1}", result)
    result = re.sub(r"\^([A-Za-z0-9])(?=[^A-Za-z0-9{])", r"^{\1}", result)
    # Convert "{ ... }_{..}^{..}" (LaTeX-style set-builder) to use \bigl/\bigr
    # so that subscript+superscript attach to the whole group cleanly without
    # tripping "double subscript" via an inner _i. Skip when the '{' is the
    # argument of a LaTeX command (preceded by \word).
    set_builder_pat = re.compile(
        r"(?<!\\)(?<![A-Za-z])\{([^{}]+(?:\{[^{}]*\}[^{}]*)*)\}"
        r"((?:_\{[^{}]*\}|\^\{[^{}]*\}|_[A-Za-z0-9]|\^[A-Za-z0-9])+)"
    )
    def _set_builder(m):
        # Reject if the char before '{' is a letter (i.e., '\cmd{...}')
        return r"\bigl\{" + m.group(1) + r"\bigr\}" + m.group(2)
    # We need a more reliable lookbehind: ensure no '\command' immediately
    # precedes. Build using a scan.
    out_chars = []
    i = 0
    n = len(result)
    while i < n:
        if result[i] == '{':
            # Skip if the '{' is the argument of (a) a LaTeX command like
            # '\tilde{...}' OR (b) a subscript/superscript like 'X_{...}' /
            # 'X^{...}' / '10^{-13}'. In all those cases, the brace group
            # belongs to a math expression and must not be wrapped in
            # \bigl\{ ... \bigr\}.
            prev = result[i - 1] if i > 0 else ''
            if prev in ('_', '^'):
                out_chars.append(result[i])
                i += 1
                continue
            k = i - 1
            while k >= 0 and result[k].isalpha():
                k -= 1
            if k >= 0 and result[k] == '\\' and k < i - 1:
                out_chars.append(result[i])
                i += 1
                continue
            m = set_builder_pat.match(result, i)
            if m:
                out_chars.append(r"\bigl\{" + m.group(1) + r"\bigr\}" + m.group(2))
                i = m.end()
                continue
        out_chars.append(result[i])
        i += 1
    result = ''.join(out_chars)
    return result


def _wrap_math_runs(text: str) -> str:
    """Find contiguous math runs in TEXT (lines containing math glyphs) and
    emit '$ ... $' around them with proper LaTeX inside. Each line is
    processed independently to avoid swallowing prose across line breaks.
    """
    new_lines = []
    for line in text.split('\n'):
        # Quick reject
        if not any(c in line for c in _MATH_GLYPH_CHARS) and _COMBINING_TILDE not in line:
            new_lines.append(line)
            continue

        result = []
        i = 0
        n = len(line)
        while i < n:
            if not (_is_glyph(line[i]) or
                    (i + 1 < n and line[i + 1] == _COMBINING_TILDE)):
                result.append(line[i])
                i += 1
                continue
            # Start of math run. Left-extend to absorb an immediately
            # adjacent identifier head (e.g., 'h' in 'h(xᵢ)' or 'p' in 'pᵢ')
            # or a literal '{' that begins a LaTeX-style group.
            start = i
            while (start > 0
                   and (line[start - 1].isalnum() or line[start - 1] == '{')
                   and result
                   and result[-1] == line[start - 1]):
                start -= 1
                result.pop()
            # Right-extend. Stop at the first whitespace; cross-token gaps
            # are merged later by the adjacent-math coalescer.
            j = i
            while j < n:
                c = line[j]
                if _is_glyph(c) or c == _COMBINING_TILDE or c in _MATH_CHARS:
                    j += 1
                    continue
                break
            run_end = j
            # Trim trailing punctuation that should stay in prose.
            while run_end > start and line[run_end - 1] in ' .,;:':
                run_end -= 1
            run = line[start:run_end]
            trailing = line[run_end:j]
            converted = _convert_math_run(run).strip()
            if converted:
                result.append('$' + converted + '$')
            result.append(trailing)
            i = j
        new_lines.append(''.join(result))
    return '\n'.join(new_lines)


def _coalesce_math(text: str) -> str:
    """Merge '$..$<short gap>$..$' into a single '$.. <gap> ..$' so that
    adjacent math runs separated only by space (or short math-glue) become
    one inline-math island.
    """
    pattern = re.compile(
        r"\$([^$\n]+?)\$([ \t=+\-*/,\.|^_\\]{1,3})\$([^$\n]+?)\$"
    )
    prev = None
    while prev != text:
        prev = text
        text = pattern.sub(lambda m: f"${m.group(1)}{m.group(2)}{m.group(3)}$", text)
    # Also collapse adjacent inline math with zero gap ('$X$$Y$' -> '$XY$')
    # which LaTeX would otherwise parse as the start of display math ($$...$$).
    zero_pat = re.compile(r"\$([^$\n]+?)\$\$([^$\n]+?)\$")
    prev = None
    while prev != text:
        prev = text
        text = zero_pat.sub(lambda m: f"${m.group(1)}{m.group(2)}$", text)
    # Absorb a left brace immediately preceding an inline-math island when
    # the math is followed by '}_{..}' or '}^{..}'. Handles literal LaTeX
    # constructs like "{g̃ᵢ}_{i=1}^N" that survive as "{ $..$ }_{..}^N".
    brace_pat = re.compile(
        r"\{\$([^$\n]+?)\$\}((?:_\{[^{}\n]*\}|\^\{[^{}\n]*\}|\^[A-Za-z0-9]|_[A-Za-z0-9])+)"
    )
    text = brace_pat.sub(lambda m: f"$\\{{{m.group(1)}\\}}{m.group(2)}$", text)
    return text


# Set of LaTeX command names this converter actually emits or relies on.
# Any '\<name>' in prose that is NOT in this set is treated as a stray
# backslash sequence (e.g., '\n' from raw Python strings) and escaped.
_KNOWN_LATEX_CMDS = frozenset({
    'textbf', 'textit', 'texttt', 'textbackslash', 'tilde', 'bigl', 'bigr',
    'mathbb', 'mathrm', 'mathit', 'mathop', 'mathcal', 'mathfrak',
    'nabla', 'ell', 'cdot', 'otimes', 'in', 'notin', 'subset', 'supset',
    'cup', 'cap', 'emptyset', 'sum', 'prod', 'int', 'partial', 'infty',
    'sqrt', 'rightarrow', 'leftarrow', 'leftrightarrow', 'langle', 'rangle',
    'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
    'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma',
    'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
    'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Phi',
    'Psi', 'Omega',
    'leq', 'geq', 'neq', 'approx', 'pm', 'times', 'div',
    'citep', 'citet', 'cite', 'ref', 'label', 'url', 'href',
    'section', 'subsection', 'subsubsection', 'paragraph',
    'begin', 'end', 'item', 'caption', 'centering', 'includegraphics',
    'toprule', 'midrule', 'bottomrule', 'resizebox', 'dimexpr', 'relax',
    'columnwidth', 'columnsep', 'textwidth', 'linewidth',
    'ldots', 'newblock', 'bibitem', 'thebibliography', 'bibliographystyle',
    'bibliography', 'nocite', 'input', 'documentclass', 'usepackage',
    'noindent', 'newline', 'par', 'hline', 'multicolumn', 'multirow',
    'frac', 'sum', 'lim', 'log', 'exp', 'sin', 'cos', 'tan',
    'left', 'right', 'big', 'Big', 'bigg', 'Bigg',
    'text', 'mathbf', 'overline', 'underline', 'hat', 'bar', 'vec',
    'operatorname', 'mathsf', 'mathtt', 'star', 'ast', 'circ',
    'forall', 'exists',
    'icml', 'icmltitle', 'icmltitlerunning', 'icmlauthor', 'icmlauthorlist',
    'icmlaffiliation', 'icmlcorrespondingauthor', 'icmlkeywords',
    'icmlsetsymbol', 'printAffiliationsAndNotice', 'twocolumn', 'vskip',
})


def _escape_stray_backslashes(text: str) -> str:
    """In prose (outside $...$), replace '\\<word>' that is NOT a known
    LaTeX command with '\\textbackslash <word>' so raw strings like
    '\\nAnswer:' don't crash the compiler.
    """
    out = []
    in_math = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == '$':
            in_math = not in_math
            out.append(ch)
            i += 1
            continue
        if not in_math and ch == '\\' and i + 1 < n:
            # Skip already-escaped specials: \_  \%  \&  \#  \$  \{  \}
            nxt = text[i + 1]
            if nxt in '_%&#${}\\ ':
                out.append(text[i:i + 2])
                i += 2
                continue
            # Collect ASCII-letter command name
            j = i + 1
            while j < n and text[j].isalpha():
                j += 1
            name = text[i + 1:j]
            if name and name not in _KNOWN_LATEX_CMDS:
                out.append(r'\textbackslash ')
                out.append(name)
                i = j
                continue
            out.append(text[i:j or i + 1])
            i = j or i + 1
            continue
        out.append(ch)
        i += 1
    return ''.join(out)


def _escape_identifier_underscores(text: str) -> str:
    """Escape `_` outside $...$ math when it sits between alphanumerics.
    Leaves LaTeX commands (preceded by backslash) and math islands alone.
    """
    out = []
    in_math = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == '\\' and i + 1 < n:
            out.append(text[i:i + 2])
            i += 2
            continue
        if ch == '$':
            in_math = not in_math
            out.append(ch)
            i += 1
            continue
        if not in_math and ch == '_':
            prev_ch = text[i - 1] if i > 0 else ''
            nxt_ch = text[i + 1] if i + 1 < n else ''
            if prev_ch.isalnum() and nxt_ch.isalnum():
                out.append('\\_')
                i += 1
                continue
        out.append(ch)
        i += 1
    return ''.join(out)


def _wrap_bare_latex_subscripts(text: str) -> str:
    """Markdown often contains raw LaTeX-like math tokens (e.g. H_{t+1}, A_t,
    x^2) outside any $...$ wrapper. LaTeX rejects these in text mode. Detect
    them and surround with $...$, while leaving anything already inside a
    math island untouched.
    """
    # Patterns:
    #   - any letter with a braced subscript/superscript: X_{...}, x^{...}
    #   - an UPPERCASE letter with a single-char sub/superscript: H_t, X^2
    # Lowercase + single-char is ambiguous with prose identifiers (e.g.
    # h_norm_std_ratio) and is therefore NOT auto-wrapped.
    # A token must contain at least one braced sub/superscript (the
    # unambiguous LaTeX marker) OR start with an uppercase letter followed
    # by a single-char subscript not followed by more letters (H_t, X^2)
    # OR start with a digit and use '^' (numeric powers like 10^4, 2^{-7}).
    # Identifiers without any braced LaTeX (h_norm) are left alone.
    token = re.compile(
        r"("
        # set-builder group with subscript/superscript: {(...)}_{i=1}^N
        r"\{[^{}\n]+\}(?:[_^]\{[^{}\n]*\}|[_^][A-Za-z0-9])+"
        # identifier (possibly with escaped underscores) + braced sub/sup
        r"|\b[A-Za-z][A-Za-z0-9]*(?:(?:_|\\_)[A-Za-z0-9]+)*"
        r"(?:[_^]\{[^{}\n]*\})"
        r"(?:[_^]\{[^{}\n]*\}|[_^][A-Za-z0-9])*"
        # identifier already escaped (h\_norm) followed by raw ^... (carat is unambiguous)
        r"|\b[A-Za-z][A-Za-z0-9]*(?:\\_[A-Za-z0-9]+)+\^[A-Za-z0-9]+"
        r"|\b[A-Z](?:[_^][A-Za-z0-9])+(?![A-Za-z])"
        r"|\b[A-Za-z]\^[A-Za-z0-9](?![A-Za-z])"
        r"|\b[A-Za-z]\^[A-Za-z]+(?![A-Za-z])"
        r"|\b[A-Za-z]\^\{[^{}\n]*\}"
        r"|\b[0-9]+\^\{[^{}\n]*\}"
        r"|\b[0-9]+\^-?[0-9]+(?![A-Za-z])"
        r")"
    )
    out = []
    in_math = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == '\\' and i + 1 < n:
            out.append(text[i:i + 2])
            i += 2
            continue
        if ch == '$':
            in_math = not in_math
            out.append(ch)
            i += 1
            continue
        if not in_math:
            m = token.match(text, i)
            if m and m.start() == i:
                out.append('$' + m.group(0) + '$')
                i = m.end()
                continue
        out.append(ch)
        i += 1
    return ''.join(out)


def _replace_unicode(text):
    """Replace Unicode characters with LaTeX equivalents."""
    # First, fold math runs (sequences containing math glyphs) into $..$.
    text = _wrap_math_runs(text)
    # Merge adjacent inline math islands separated by short glue.
    text = _coalesce_math(text)
    # Then apply the simple table for any remaining stray unicode chars
    # (e.g. quotes, dashes, ellipsis, isolated Greek in prose). Inside an
    # existing $...$ island, replace '$\eta$' -> '\eta' (raw form) so we
    # don't fragment the surrounding island with extra dollar signs.
    def _apply_unicode(seg, in_math):
        for char, latex in UNICODE_TO_LATEX.items():
            if in_math and latex.startswith('$') and latex.endswith('$'):
                seg = seg.replace(char, latex[1:-1])
            else:
                seg = seg.replace(char, latex)
        return seg
    out_parts = []
    i = 0
    in_math = False
    while i < len(text):
        if text[i] == '$':
            in_math = not in_math
            out_parts.append(text[i])
            i += 1
            continue
        out_parts.append(_apply_unicode(text[i], in_math))
        i += 1
    text = ''.join(out_parts)
    # Wrap any bare X_{...} / X^{...} / X_a / X^2 tokens that slipped through.
    text = _wrap_bare_latex_subscripts(text)
    # Re-coalesce in case the new tokens border existing math islands.
    text = _coalesce_math(text)
    # Combine consecutive single-char super/subscripts inside any inline
    # math island. E.g. '$10^-^1^3$' -> '$10^{-13}$'.
    def _combine_in_math(seg, prefix):
        pat = re.compile(rf"((?:\{prefix}[\-+0-9])(?:\{prefix}[\-+0-9])+)")
        return pat.sub(
            lambda m: f"{prefix}{{" + ''.join(
                m.group(1)[i + 1] for i in range(0, len(m.group(1)), 2)
            ) + "}",
            seg,
        )
    text = re.sub(
        r"\$([^$\n]+?)\$",
        lambda m: '$' + _combine_in_math(_combine_in_math(m.group(1), '^'), '_') + '$',
        text,
    )
    # Absorb '$X$_word' / '$X$^word' (raw subscript/superscript immediately
    # after a closed math island) back into the island as '$X_{word}$'.
    text = re.sub(
        r"\$([^$\n]+?)\$_([A-Za-z][A-Za-z0-9]*)",
        lambda m: f"${m.group(1)}_{{{m.group(2)}}}$",
        text,
    )
    text = re.sub(
        r"\$([^$\n]+?)\$\^([A-Za-z0-9][A-Za-z0-9]*)",
        lambda m: f"${m.group(1)}^{{{m.group(2)}}}$",
        text,
    )
    # If a single non-empty line is dominated by math tokens / fragments
    # (heuristic: >=2 inline-math islands or contains '\Sigma'/'\sigma'/etc),
    # wrap the entire line in display math by stitching all islands and
    # in-between text into one $...$ expression. This rescues lines like
    # "r\_eff(W, $\tau$) = min{r : $\Sigma_i \sigma_i^2 \geq \tau$}".
    def _wrap_math_heavy_line(ln):
        # Skip lines that already have control structures we can't put in math.
        if '$$' in ln or '\\begin' in ln or '\\end' in ln or '\\item' in ln:
            return ln
        if '\\textbf' in ln or '\\textit' in ln or '\\texttt' in ln:
            return ln
        if '\\citep' in ln or '\\cite' in ln:
            return ln
        # Markdown bold/italic markers are processed AFTER this; if present,
        # wrapping would put them inside math mode and break the conversion.
        if '**' in ln or ln.count('*') >= 2:
            return ln
        # Strong heuristic: the WHOLE line should look like an equation.
        # Reject if it contains common English words (more than 2-letter
        # word followed by a space) that strongly suggest prose.
        prose_word_re = re.compile(
            r'\b(?:the|of|and|is|with|where|for|by|to|in|at|on|that|this'
            r'|consistency|threshold|than|required|below|above)\b',
            re.IGNORECASE,
        )
        if prose_word_re.search(ln):
            return ln
        # Require a really clear math signal: a Sigma/sum/frac/etc. operator.
        triggers = (r'\Sigma', r'\sigma_', r'\sum', r'\prod', r'\int',
                    r'\frac', r'\partial', r'\nabla')
        if not any(t in ln for t in triggers):
            return ln
        # Strip $ delimiters; require composition to be mostly math-safe.
        stripped = ln.replace('$', '')
        non_math = sum(1 for c in stripped
                       if c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                    '0123456789+-*/=,()[]{}|^_.\\: \t')
        if non_math > 4:
            return ln
        first_dollar = ln.find('$')
        prefix = ln[:first_dollar].strip() if first_dollar >= 0 else ln.strip()
        if len(prefix.split()) > 3:
            return ln
        return '$' + stripped.strip() + '$'
    text = '\n'.join(_wrap_math_heavy_line(ln) for ln in text.split('\n'))
    # Escape underscores in identifier-like prose tokens.
    text = _escape_identifier_underscores(text)
    # Escape stray backslash sequences (e.g., raw \n from Python strings).
    text = _escape_stray_backslashes(text)
    return text


def _escape_latex_text(text):
    """Escape LaTeX special characters in regular text."""
    if not text:
        return text
    # Don't escape inside math mode
    if text.strip().startswith('$'):
        return text
    replacements = [
        ('%', r'\%'),
        ('&', r'\&'),
        ('#', r'\#'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    text = _replace_unicode(text)
    return text


_DISPLAY_MATH_RE = re.compile(r"\$\$.+?\$\$", re.DOTALL)


def _convert_inline(line):
    """Convert inline markdown formatting to LaTeX."""
    # Protect $$...$$ display-math segments from any unicode/escape rewrites,
    # so we don't insert inner $...$ that would prematurely close $$.
    displays = []
    def _stash(m):
        displays.append(m.group(0))
        return f"\x00DM{len(displays) - 1}\x00"
    line = _DISPLAY_MATH_RE.sub(_stash, line)
    # IMPORTANT: handle unicode math BEFORE wrapping content in \textbf{} /
    # \textit{} / \texttt{}, so the math-run detector sees raw markdown and
    # cannot mistake the wrapper's braces for math content.
    line = _replace_unicode(line)
    # Bold (with optional immediate subscript: **s**_m -> \textbf{s}$_{m}$)
    def _bold_sub(m):
        body = m.group(1)
        sub = m.group(2)
        sup = m.group(3)
        out = r'\textbf{' + body + '}'
        if sub:
            out += '$_{' + sub + '}$'
        if sup:
            out += '$^{' + sup + '}$'
        return out
    line = re.sub(
        r"\*\*([^*]+)\*\*(?:_([A-Za-z0-9]+))?(?:\^([A-Za-z0-9]+))?",
        _bold_sub,
        line,
    )
    # Italic
    line = re.sub(r'\*([^*]+)\*', r'\\textit{\1}', line)
    # Inline code: escape characters that LaTeX would interpret as commands
    # inside the \texttt{} argument. Use a sentinel for backslash so it is
    # not re-escaped by the subsequent brace replacements.
    def _ttesc(m):
        body = m.group(1)
        _BS = '\x00BS\x00'
        body = body.replace('\\', _BS)
        body = (body.replace('{', r'\{').replace('}', r'\}')
                    .replace('%', r'\%').replace('&', r'\&')
                    .replace('#', r'\#').replace('$', r'\$')
                    .replace('^', r'\^{}').replace('~', r'\~{}')
                    .replace('_', r'\_'))
        body = body.replace(_BS, r'\textbackslash ')
        return r'\texttt{' + body + '}'
    line = re.sub(r'`([^`]+)`', _ttesc, line)
    # Citations: support both [Author, Year] and (Author, Year) styles,
    # including "et al.", "and", and "&" connectors. Resolve to the actual
    # bib key when an index is available (BIB_KEY_INDEX); otherwise fall
    # back to the legacy AuthorYear synthesis.
    def _cite_key(author_token: str, year: str) -> str:
        # Strip whitespace; first word is the first author's last name.
        first = re.split(r"[\s,]+", author_token.strip(), maxsplit=1)[0]
        first = re.sub(r"[^A-Za-z]", "", first)
        prefix = f"{first}{year}"
        idx = BIB_KEY_INDEX.get(prefix)
        if idx:
            return idx
        return prefix
    cite_pat = re.compile(
        r"[\[\(]"
        r"([A-Z][A-Za-z\-]+"
        r"(?:\s+et\s+al\.?|\s+(?:and|&)\s+[A-Z][A-Za-z\-]+)?)"
        r",?\s+(\d{4})"
        r"[\]\)]"
    )
    line = cite_pat.sub(
        lambda m: r'\citep{' + _cite_key(m.group(1), m.group(2)) + '}',
        line,
    )
    line = _escape_latex_text(line)
    # Restore protected $$...$$ display-math segments verbatim.
    for i, raw in enumerate(displays):
        line = line.replace(f"\x00DM{i}\x00", raw)
    return line


# Populated by build_bib_index() when generate_latex_project runs.
BIB_KEY_INDEX: dict = {}


def _copy_bib_sanitized(src_path, dst_path):
    """Copy a .bib file, with two cleanups:
      1) Drop `note = {...}` fields entirely (these often contain prose
         like "UNVERIFIED: ..." with raw '_' that would crash LaTeX, and
         users typically don't want them in the printed bibliography).
      2) Escape raw '_' in remaining field values so LaTeX won't interpret
         them as math subscripts. Entry-header lines ("@type{Key,") are
         left untouched.
    """
    with open(src_path, encoding="utf-8") as fh:
        text = fh.read()

    # Step 1: strip note fields. They may span multiple lines until the
    # matching closing brace. We track brace depth from the start of the
    # field value.
    cleaned = []
    i = 0
    n = len(text)
    note_re = re.compile(r"(?im)^[ \t]*note[ \t]*=[ \t]*\{")
    while i < n:
        m = note_re.match(text, i)
        if m:
            # Find the matching '}' from m.end()-1 (which is the opening '{').
            depth = 1
            j = m.end()
            while j < n and depth:
                ch = text[j]
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                j += 1
            # Also consume an optional trailing ',' and newline so we don't
            # leave a dangling comma.
            while j < n and text[j] in ', \t':
                j += 1
            if j < n and text[j] == '\n':
                j += 1
            i = j
            continue
        # Copy until next newline (regex matches at line start)
        nl = text.find('\n', i)
        if nl < 0:
            cleaned.append(text[i:])
            break
        cleaned.append(text[i:nl + 1])
        i = nl + 1
    text = ''.join(cleaned)

    # Step 1.5: drop entire entries whose author field is a placeholder
    # like '[Author(s) unknown]' or '[CITATION NEEDED]'. Such entries
    # produce a malformed `\bibitem[Anonymous(year)]{key}` short label
    # that natbib mis-parses and rejects with
    # "Bibliography not compatible with author-year citations".
    entry_re = re.compile(
        r"(@\w+\{[^,]+,(?:[^@]|\n)*?\n\s*\}\s*\n?)",
        re.MULTILINE,
    )
    # Match any entry whose author field contains a '[...]' placeholder
    # anywhere (whole-field OR partial like 'Gupta and [CITATION NEEDED]').
    placeholder_re = re.compile(
        r"author\s*=\s*\{[^}]*\[[A-Z][^\]]*\][^}]*\}",
        re.IGNORECASE,
    )
    kept = []
    for m in entry_re.finditer(text):
        entry = m.group(1)
        if placeholder_re.search(entry):
            continue
        kept.append(entry)
    # Preserve any preamble (comments before first @entry).
    first_at = text.find('@')
    preamble = text[:first_at] if first_at >= 0 else ''
    text = preamble + ''.join(kept)

    # Step 2: escape raw '_' in field values and neutralize placeholders
    # like '[CITATION NEEDED]' that BibTeX cannot parse as author names.
    out_lines = []
    for line in text.split("\n"):
        if line.lstrip().startswith("@"):
            out_lines.append(line)
            continue
        # Replace any '[...]' placeholder (uppercase text in brackets) with
        # 'Anonymous, A.' — a two-token name so the BST's author parser can
        # split it into surname/given without producing a degenerate
        # '[Surname(Year)]' short label that natbib mis-parses.
        line = re.sub(r"\[[A-Z][^\]]*\]", "Anonymous, A.", line)
        # Escape underscores in remaining field bodies.
        line = re.sub(r"(?<!\\)_", r"\\_", line)
        out_lines.append(line)
    with open(dst_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out_lines))


def build_bib_index(bib_path):
    """Build {AuthorYear -> full-bib-key} index from a .bib file."""
    BIB_KEY_INDEX.clear()
    if not bib_path or not os.path.exists(bib_path):
        return
    with open(bib_path, encoding="utf-8") as fh:
        content = fh.read()
    # Each entry: @type{KEY,\n  author = {...},\n  year = {YYYY},
    entry_re = re.compile(
        r"@\w+\{([^,]+),(.*?)(?=@\w+\{|\Z)",
        re.DOTALL,
    )
    field_author = re.compile(r"author\s*=\s*\{([^}]+)\}", re.IGNORECASE)
    field_year = re.compile(r"year\s*=\s*\{?(\d{4})\}?", re.IGNORECASE)
    for m in entry_re.finditer(content):
        key = m.group(1).strip()
        body = m.group(2)
        am = field_author.search(body)
        ym = field_year.search(body)
        if not am or not ym:
            continue
        author_field = am.group(1)
        # First author is "LastName, First..." -> take chars before first comma
        first_author = author_field.split(",")[0].strip()
        first_last = re.sub(r"[^A-Za-z]", "", first_author.split()[-1] if first_author else "")
        if not first_last:
            continue
        year = ym.group(1)
        prefix = f"{first_last}{year}"
        # Prefer the first match if multiple entries share a prefix.
        BIB_KEY_INDEX.setdefault(prefix, key)


# ============================================================
# Section splitting
# ============================================================

SECTION_MAP = {
    'abstract': 'abstract',
    'introduction': 'introduction',
    'related work': 'related_work',
    'method': 'methodology',
    'methodology': 'methodology',
    'experimental setup': 'experiments',
    'experiments': 'experiments',
    'results': 'results',
    'discussion': 'discussion',
    'conclusion': 'conclusion',
    'conclusions': 'conclusion',
    'references': 'references',
}


def split_into_sections(paper_md):
    """Split paper into sections based on ## headers."""
    lines = paper_md.split('\n')
    title = "Untitled Paper"

    # Find title (first # header)
    for line in lines:
        if line.startswith('# ') and not line.startswith('## '):
            title = line[2:].strip()
            break

    # Find section boundaries (## headers)
    section_starts = []
    for i, line in enumerate(lines):
        if line.startswith('## '):
            section_name = line[3:].strip()
            # Remove numbering
            section_name_clean = re.sub(r'^\d+\.\s*', '', section_name)
            section_starts.append((i, section_name_clean))

    # Extract sections
    sections = {}
    for idx, (start, name) in enumerate(section_starts):
        end = section_starts[idx + 1][0] if idx + 1 < len(section_starts) else len(lines)
        content = '\n'.join(lines[start + 1:end])
        key = SECTION_MAP.get(name.lower(), name.lower().replace(' ', '_'))
        sections[key] = content

    return title, sections


# ============================================================
# LaTeX project generation
# ============================================================

MAIN_TEX_TEMPLATE = r"""\documentclass{{article}}

% ICML 2025 style
\usepackage{{icml2025}}

% Unicode support (xelatex)
\usepackage{{fontspec}}

% Standard packages
\usepackage{{microtype}}
\usepackage{{graphicx}}
\usepackage{{subfigure}}
\usepackage{{booktabs}}
\usepackage{{hyperref}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{algorithm}}
\usepackage{{algorithmic}}
\usepackage{{multirow}}
\usepackage{{makecell}}
\usepackage{{array}}
\usepackage{{natbib}}

\icmltitlerunning{{{short_title}}}

\begin{{document}}

\twocolumn[
\icmltitle{{{title}}}

\icmlsetsymbol{{equal}}{{*}}

\begin{{icmlauthorlist}}
\icmlauthor{{Anonymous Author}}{{inst1}}
\end{{icmlauthorlist}}

\icmlaffiliation{{inst1}}{{Anonymous Institution}}

\icmlcorrespondingauthor{{Anonymous Author}}{{anonymous@anonymous.org}}

\icmlkeywords{{Machine Learning, ICML}}

\vskip 0.3in
]

\printAffiliationsAndNotice{{}}

% Abstract
\begin{{abstract}}
\input{{sections/abstract}}
\end{{abstract}}

% Main sections
\section{{Introduction}}
\input{{sections/introduction}}

\section{{Related Work}}
\input{{sections/related_work}}

\section{{Methodology}}
\input{{sections/methodology}}

\section{{Experimental Setup}}
\input{{sections/experiments}}

\section{{Results}}
\input{{sections/results}}

\section{{Discussion}}
\input{{sections/discussion}}

\section{{Conclusion}}
\input{{sections/conclusion}}

% References
% Emit every entry from references.bib, even those not cited inline.
\nocite{{*}}
\bibliographystyle{{icml2025}}
\bibliography{{references}}

\end{{document}}
"""


_ICML2025_KIT_URLS = (
    "https://media.icml.cc/Conferences/ICML2025/Styles/icml2025.zip",
    "https://icml.cc/Conferences/2025/Styles/icml2025.zip",
)


def _ensure_icml_style(output_dir, placeholder_max=1024):
    """Make sure icml2025.sty/.bst in OUTPUT_DIR are real (not placeholder).

    If missing or too small, try to download the official ICML 2025
    author kit and extract the two files. Silently no-op on network
    failure — the subsequent xelatex pass will report a missing-style
    error so the user can see it.
    """
    import urllib.request
    import zipfile
    import io

    def _is_real_sty(p):
        if not os.path.exists(p) or os.path.getsize(p) < placeholder_max:
            return False
        # Real ICML 2025 sty defines \icmltitlerunning (or has reasonable
        # size). Accept either signal.
        try:
            with open(p, encoding='utf-8', errors='ignore') as fh:
                return 'icmltitlerunning' in fh.read() or os.path.getsize(p) >= 10000
        except OSError:
            return False

    def _is_real_bst(p):
        return os.path.exists(p) and os.path.getsize(p) >= placeholder_max

    sty_path = os.path.join(output_dir, 'icml2025.sty')
    bst_path = os.path.join(output_dir, 'icml2025.bst')
    if _is_real_sty(sty_path) and _is_real_bst(bst_path):
        return

    # Drop any placeholder/incomplete versions so TeXLive can't see them.
    for p, ok in ((sty_path, _is_real_sty(sty_path)),
                  (bst_path, _is_real_bst(bst_path))):
        if os.path.exists(p) and not ok:
            try:
                os.remove(p)
            except OSError:
                pass

    for url in _ICML2025_KIT_URLS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "md_to_pdf"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                blob = resp.read()
            with zipfile.ZipFile(io.BytesIO(blob)) as zf:
                for member in zf.namelist():
                    base = os.path.basename(member)
                    if base in ('icml2025.sty', 'icml2025.bst'):
                        with zf.open(member) as src, \
                             open(os.path.join(output_dir, base), 'wb') as dst:
                            dst.write(src.read())
            if _is_real('icml2025.sty') and _is_real('icml2025.bst'):
                print(f"    Downloaded ICML 2025 style files from {url}")
                return
        except Exception as e:  # noqa: BLE001
            print(f"    (style download from {url} failed: {e})")
            continue


def generate_latex_project(md_path, output_dir, figures_dir=None, bib_path=None, style_source=None):
    """Generate a complete LaTeX project from a Markdown paper."""
    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        paper_md = f.read()

    # Create output structure
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'sections'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'figures'), exist_ok=True)

    # Build bib key index BEFORE converting the body so that
    # _convert_inline() can resolve (Author, Year) -> real bib key.
    build_bib_index(bib_path)

    # Split and convert
    title, sections = split_into_sections(paper_md)
    short_title = title[:60] + '...' if len(title) > 60 else title

    print(f"  Title: {title}")
    print(f"  Found {len(sections)} sections: {list(sections.keys())}")

    # Write section .tex files
    for section_name, content in sections.items():
        if section_name == 'references':
            continue
        latex_content = convert_markdown_to_latex(content)
        tex_path = os.path.join(output_dir, 'sections', f'{section_name}.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        print(f"    Created sections/{section_name}.tex")

    # Ensure all expected section files exist (empty if missing)
    expected = ['abstract', 'introduction', 'related_work', 'methodology',
                'experiments', 'results', 'discussion', 'conclusion']
    for sec in expected:
        tex_path = os.path.join(output_dir, 'sections', f'{sec}.tex')
        if not os.path.exists(tex_path):
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(f'% Section {sec} not found in source paper\n')
            print(f"    Created empty sections/{sec}.tex (not in source)")

    # Generate main.tex
    main_tex = MAIN_TEX_TEMPLATE.format(title=title, short_title=short_title)
    with open(os.path.join(output_dir, 'main.tex'), 'w', encoding='utf-8') as f:
        f.write(main_tex)
    print(f"    Created main.tex")

    # Copy references.bib, sanitizing field bodies for LaTeX compatibility
    # (e.g., escape raw '_' inside note/title fields that would otherwise
    # crash xelatex with "Missing $ inserted").
    if bib_path and os.path.exists(bib_path):
        out_bib = os.path.join(output_dir, 'references.bib')
        _copy_bib_sanitized(bib_path, out_bib)
        print(f"    Copied references.bib from {bib_path}")
    else:
        # Create empty bib
        with open(os.path.join(output_dir, 'references.bib'), 'w') as f:
            f.write('% No references available\n')
        print(f"    Created empty references.bib")

    # Copy figures
    if figures_dir and os.path.isdir(figures_dir):
        fig_count = 0
        for fig in os.listdir(figures_dir):
            src = os.path.join(figures_dir, fig)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(output_dir, 'figures', fig))
                fig_count += 1
        print(f"    Copied {fig_count} figures")

    # Copy ICML style files from existing overleaf if available. Skip any
    # source file that is a placeholder (under 1 KB — real ICML2025 sty is
    # ~28 KB, real fancyhdr ~10 KB, etc.). If our local copy ends up
    # missing icml2025.sty/.bst we attempt to download the official ICML
    # 2025 author kit from a known mirror. Smaller helpers (fancyhdr,
    # algorithm, algorithmic) live in TeXLive, so skipping them is safe.
    PLACEHOLDER_MAX = 1024
    if style_source and os.path.isdir(style_source):
        style_files = ['icml2025.sty', 'icml2025.bst', 'fancyhdr.sty',
                       'algorithm.sty', 'algorithmic.sty']
        for sf in style_files:
            src = os.path.join(style_source, sf)
            if not os.path.exists(src):
                continue
            if os.path.getsize(src) < PLACEHOLDER_MAX:
                continue  # placeholder file — let TeXLive provide it
            # Extra check for icml2025.sty: it must actually define
            # \icmltitlerunning, otherwise it's an older/wrong variant.
            if sf == 'icml2025.sty':
                try:
                    with open(src, encoding='utf-8', errors='ignore') as fh:
                        body = fh.read()
                    if 'icmltitlerunning' not in body:
                        continue
                except OSError:
                    continue
            shutil.copy2(src, os.path.join(output_dir, sf))
        print(f"    Copied style files from {style_source}")

    # Remove any pre-existing placeholder sty files in the output dir so
    # LaTeX doesn't prefer them over the system TeXLive copies.
    for sf in ('fancyhdr.sty', 'algorithm.sty', 'algorithmic.sty'):
        p = os.path.join(output_dir, sf)
        if os.path.exists(p) and os.path.getsize(p) < PLACEHOLDER_MAX:
            try:
                os.remove(p)
            except OSError:
                pass

    # Last-resort: if icml2025.sty or .bst still missing/placeholder,
    # try to fetch the official ICML 2025 author kit.
    _ensure_icml_style(output_dir, placeholder_max=PLACEHOLDER_MAX)

    return True


# ============================================================
# PDF compilation
# ============================================================

def _run_xelatex_passes(output_dir):
    """Run xelatex+bibtex+xelatex+xelatex. Return (rc_of_last, stdout)."""
    pdflatex_cmd = ['xelatex', '-interaction=nonstopmode', '-halt-on-error',
                    '-file-line-error', 'main.tex']
    bibtex_cmd = ['bibtex', 'main']
    try:
        r1 = subprocess.run(pdflatex_cmd, cwd=output_dir, capture_output=True,
                            text=True, timeout=180)
        subprocess.run(bibtex_cmd, cwd=output_dir, capture_output=True,
                       text=True, timeout=60)
        subprocess.run(pdflatex_cmd, cwd=output_dir, capture_output=True,
                       text=True, timeout=180)
        r = subprocess.run(pdflatex_cmd, cwd=output_dir, capture_output=True,
                           text=True, timeout=180)
        return r.returncode, (r1.stdout or '') + (r.stdout or '')
    except subprocess.TimeoutExpired as e:
        return -1, f"TIMEOUT: {e}"


def _extract_latex_errors(output_dir):
    """Pull file:line: prefixed error lines from main.log, return up to 10."""
    log_path = os.path.join(output_dir, 'main.log')
    if not os.path.exists(log_path):
        return []
    out = []
    try:
        with open(log_path, encoding='utf-8', errors='ignore') as fh:
            lines = fh.readlines()
    except OSError:
        return []
    for i, ln in enumerate(lines):
        # file:line: error  OR  starts with '! '
        if re.match(r"^\./[^:]+:\d+:", ln) or ln.startswith('! '):
            ctx = ''.join(lines[i:i + 5])
            out.append(ctx.strip())
        if len(out) >= 10:
            break
    return out


def _claude_repair_tex(output_dir, errors, attempt):
    """Ask Claude CLI to fix the .tex files in OUTPUT_DIR based on ERRORS.
    Returns True if Claude reported success and at least one .tex was modified.
    """
    if shutil.which('claude') is None:
        print("  claude CLI not available; skipping auto-repair.")
        return False

    err_block = '\n\n'.join(errors[:8]) or '(no specific error captured)'
    prompt = (
        "You are fixing LaTeX compile errors in a paper refinement. The working "
        "directory is the current one. Read main.log to confirm the errors, "
        f"then edit the relevant files under sections/ (and main.tex if needed) "
        "to make `xelatex main.tex` compile without `!` errors. Do not rename "
        "files, do not add new packages, do not change \\documentclass. Make "
        "minimal targeted edits: wrap stray math tokens in $...$, escape "
        "underscores in prose, fix unmatched braces, etc. When you finish, "
        "print the single word DONE on its own line.\n\n"
        f"=== Compile errors (attempt {attempt}) ===\n{err_block}\n"
    )

    # Snapshot mtimes so we can detect any actual edits.
    tex_files = []
    for root, _, files in os.walk(output_dir):
        for f in files:
            if f.endswith('.tex'):
                tex_files.append(os.path.join(root, f))
    before = {p: os.path.getmtime(p) for p in tex_files}

    import time
    proc = None
    for retry in range(3):
        try:
            proc = subprocess.run(
                ['claude', '-p', '--permission-mode', 'acceptEdits',
                 '--allowed-tools', 'Read,Edit,Write,Bash'],
                cwd=output_dir,
                input=prompt,
                capture_output=True, text=True, timeout=600,
            )
        except subprocess.TimeoutExpired:
            print("  claude repair: TIMEOUT")
            return False
        combined = (proc.stdout or '') + (proc.stderr or '')
        if 'Overloaded' in combined or '529' in combined or 'rate' in combined.lower():
            wait = 15 * (retry + 1)
            print(f"  claude overloaded; retrying in {wait}s...")
            time.sleep(wait)
            continue
        break
    if proc is None:
        return False

    if proc.returncode != 0:
        print(f"  claude exited rc={proc.returncode}; stderr: {proc.stderr[:200]}")
    tail = (proc.stdout or '').strip().splitlines()
    print(f"  claude: {' | '.join(tail[-3:]) if tail else '(no output)'}")

    changed = any(
        os.path.exists(p) and os.path.getmtime(p) != before[p]
        for p in before
    )
    return changed


def compile_pdf(output_dir, max_retries=3, claude_repair=True):
    """Compile LaTeX to PDF; if it fails, optionally invoke Claude CLI to
    edit the .tex files and retry. MAX_RETRIES counts repair attempts
    (the first plain compile is always attempted).
    """
    main_tex = os.path.join(output_dir, 'main.tex')
    if not os.path.exists(main_tex):
        print(f"  ERROR: main.tex not found in {output_dir}")
        return False

    for stale in ('main.pdf', 'main.aux', 'main.bbl', 'main.blg',
                  'main.log', 'main.out', 'main.toc'):
        p = os.path.join(output_dir, stale)
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass

    print("  Compilation attempt 1 (initial)...")
    _run_xelatex_passes(output_dir)
    pdf_path = os.path.join(output_dir, 'main.pdf')

    def _ok():
        if not (os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0):
            return False
        log_path = os.path.join(output_dir, 'main.log')
        if not os.path.exists(log_path):
            return False
        try:
            log = open(log_path, encoding='utf-8', errors='ignore').read()
        except OSError:
            return False
        # Reject if any line begins with '! ' OR matches the
        # "<file>:<line>:" file-line-error format LaTeX emits.
        for ln in log.splitlines():
            if ln.startswith('! '):
                return False
            if re.match(r"^\./[^:]+:\d+:\s", ln):
                return False
        m = re.search(r"Output written on main\.pdf \((\d+) page", log)
        return bool(m) and int(m.group(1)) > 0

    if _ok():
        print(f"  PDF generated: main.pdf ({os.path.getsize(pdf_path) // 1024} KB)")
        return True

    if not claude_repair:
        print("  FAILED (claude_repair disabled).")
        return False

    for attempt in range(1, max_retries + 1):
        errs = _extract_latex_errors(output_dir)
        if not errs:
            print(f"  No log errors captured on retry {attempt}; aborting.")
            return False
        print(f"  Repair attempt {attempt}/{max_retries} via claude...")
        changed = _claude_repair_tex(output_dir, errs, attempt)
        if not changed:
            print("  Claude did not modify any .tex; aborting.")
            return False
        # Re-run compile.
        for stale in ('main.pdf', 'main.aux', 'main.bbl', 'main.blg',
                      'main.log', 'main.out', 'main.toc'):
            p = os.path.join(output_dir, stale)
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass
        _run_xelatex_passes(output_dir)
        if _ok():
            print(f"  PDF generated after repair {attempt}: "
                  f"({os.path.getsize(pdf_path) // 1024} KB)")
            return True

    print(f"  FAILED after {max_retries} repair attempts.")
    return False


# ============================================================
# Main entry point
# ============================================================

def convert(input_md, output_dir, figures_dir=None, bib_path=None, style_source=None):
    """Full pipeline: MD -> LaTeX -> PDF. Returns True if PDF was generated."""
    print(f"  Input:  {input_md}")
    print(f"  Output: {output_dir}")

    success = generate_latex_project(
        md_path=input_md,
        output_dir=output_dir,
        figures_dir=figures_dir,
        bib_path=bib_path,
        style_source=style_source,
    )

    if not success:
        return False

    return compile_pdf(output_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown paper to LaTeX (ICML 2025) and compile to PDF",
    )
    parser.add_argument("--input", required=True, help="Input Markdown file")
    parser.add_argument("--output-dir", required=True, help="Output directory for LaTeX project")
    parser.add_argument("--figures-dir", default=None, help="Directory containing figures")
    parser.add_argument("--bib", default=None, help="BibTeX references file")
    parser.add_argument("--style-source", default=None, help="Directory containing ICML style files")

    args = parser.parse_args()

    success = convert(
        input_md=args.input,
        output_dir=args.output_dir,
        figures_dir=args.figures_dir,
        bib_path=args.bib,
        style_source=args.style_source,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
