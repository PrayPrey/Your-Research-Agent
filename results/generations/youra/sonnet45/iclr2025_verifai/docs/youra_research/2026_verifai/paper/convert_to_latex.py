#!/usr/bin/env python3
"""
Convert markdown paper to LaTeX sections for Overleaf submission.
Phase 6.5.1 - Step 02: Markdown to LaTeX conversion
"""

import re
import os
from pathlib import Path

def escape_latex(text):
    """Escape special LaTeX characters."""
    # First handle Unicode math symbols with placeholders
    unicode_map = {
        '≤': '<<<LEQ>>>',
        '≥': '<<<GEQ>>>',
        '±': '<<<PM>>>',
        '×': '<<<TIMES>>>',
        '÷': '<<<DIV>>>',
        '≈': '<<<APPROX>>>',
        '≠': '<<<NEQ>>>',
        '∈': '<<<IN>>>',
        '∀': '<<<FORALL>>>',
        '∃': '<<<EXISTS>>>',
        '→': '<<<RIGHTARROW>>>',
        '←': '<<<LEFTARROW>>>',
        '↔': '<<<LEFTRIGHTARROW>>>',
        '∧': '<<<WEDGE>>>',
        '∨': '<<<VEE>>>',
        'α': '<<<ALPHA>>>',
        'β': '<<<BETA>>>',
        'γ': '<<<GAMMA>>>',
        'δ': '<<<DELTA>>>',
        'ε': '<<<EPSILON>>>',
        'θ': '<<<THETA>>>',
        'λ': '<<<LAMBDA>>>',
        'μ': '<<<MU>>>',
        'π': '<<<PI>>>',
        'σ': '<<<SIGMA>>>',
        'τ': '<<<TAU>>>',
        'φ': '<<<PHI>>>',
        'ω': '<<<OMEGA>>>',
    }

    # Replace unicode with placeholders
    for char, placeholder in unicode_map.items():
        text = text.replace(char, placeholder)

    # Order matters - backslash must be first
    replacements = [
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    # Replace placeholders with LaTeX math
    latex_map = {
        '<<<LEQ>>>': r'$\leq$',
        '<<<GEQ>>>': r'$\geq$',
        '<<<PM>>>': r'$\pm$',
        '<<<TIMES>>>': r'$\times$',
        '<<<DIV>>>': r'$\div$',
        '<<<APPROX>>>': r'$\approx$',
        '<<<NEQ>>>': r'$\neq$',
        '<<<IN>>>': r'$\in$',
        '<<<FORALL>>>': r'$\forall$',
        '<<<EXISTS>>>': r'$\exists$',
        '<<<RIGHTARROW>>>': r'$\rightarrow$',
        '<<<LEFTARROW>>>': r'$\leftarrow$',
        '<<<LEFTRIGHTARROW>>>': r'$\leftrightarrow$',
        '<<<WEDGE>>>': r'$\wedge$',
        '<<<VEE>>>': r'$\vee$',
        '<<<ALPHA>>>': r'$\alpha$',
        '<<<BETA>>>': r'$\beta$',
        '<<<GAMMA>>>': r'$\gamma$',
        '<<<DELTA>>>': r'$\delta$',
        '<<<EPSILON>>>': r'$\epsilon$',
        '<<<THETA>>>': r'$\theta$',
        '<<<LAMBDA>>>': r'$\lambda$',
        '<<<MU>>>': r'$\mu$',
        '<<<PI>>>': r'$\pi$',
        '<<<SIGMA>>>': r'$\sigma$',
        '<<<TAU>>>': r'$\tau$',
        '<<<PHI>>>': r'$\phi$',
        '<<<OMEGA>>>': r'$\omega$',
    }

    for placeholder, latex in latex_map.items():
        text = text.replace(placeholder, latex)

    return text

def convert_inline_formatting(text):
    """Convert markdown inline formatting to LaTeX."""
    # Bold: **text** -> \textbf{text}
    text = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', text)

    # Italic: *text* -> \textit{text}
    text = re.sub(r'\*([^*]+)\*', r'\\textit{\1}', text)

    # Inline code: `code` -> \texttt{code}
    text = re.sub(r'`([^`]+)`', r'\\texttt{\1}', text)

    # Citations: [Author2024] -> \cite{Author2024}
    text = re.sub(r'\[([A-Z][a-zA-Z]+\d{4}[a-zA-Z]*)\]', r'\\cite{\1}', text)

    return text

def convert_section_to_latex(section_name, content):
    """Convert a markdown section to LaTeX."""
    lines = content.strip().split('\n')
    latex_lines = []

    in_list = False
    in_code_block = False
    code_lang = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip frontmatter
        if line.strip() == '---':
            i += 1
            continue

        # Code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_lang = line.strip()[3:].strip() or 'text'
                latex_lines.append(f'\\begin{{verbatim}}')
            else:
                in_code_block = False
                latex_lines.append(f'\\end{{verbatim}}')
            i += 1
            continue

        if in_code_block:
            latex_lines.append(line)
            i += 1
            continue

        # Section headers (## or ###)
        if line.startswith('###'):
            title = line[3:].strip()
            title = convert_inline_formatting(title)
            latex_lines.append(f'\\subsubsection{{{title}}}')
            i += 1
            continue
        elif line.startswith('##'):
            title = line[2:].strip()
            title = convert_inline_formatting(title)
            latex_lines.append(f'\\subsection{{{title}}}')
            i += 1
            continue

        # Tables
        if '|' in line and line.strip().startswith('|'):
            # Extract table
            table_lines = [line]
            j = i + 1
            while j < len(lines) and '|' in lines[j]:
                table_lines.append(lines[j])
                j += 1

            # Convert table to LaTeX
            latex_lines.append(convert_table_to_latex(table_lines))
            i = j
            continue

        # Figures
        if line.strip().startswith('!['):
            match = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
            if match:
                caption = match.group(1)
                filepath = match.group(2)
                filename = os.path.basename(filepath)
                label = filename.replace('.png', '').replace('_', '-')

                latex_lines.append('\\begin{figure}[htbp]')
                latex_lines.append('\\centering')
                latex_lines.append(f'\\includegraphics[width=0.8\\textwidth]{{figures/{filename}}}')
                latex_lines.append(f'\\caption{{{caption}}}')
                latex_lines.append(f'\\label{{fig:{label}}}')
                latex_lines.append('\\end{figure}')
            i += 1
            continue

        # Lists
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                latex_lines.append('\\begin{itemize}')
                in_list = True

            item_text = line.strip()[2:].strip()
            item_text = escape_latex(item_text)
            item_text = convert_inline_formatting(item_text)
            latex_lines.append(f'  \\item {item_text}')
            i += 1
            continue
        elif in_list and line.strip() == '':
            latex_lines.append('\\end{itemize}')
            in_list = False
            i += 1
            continue

        # Regular paragraphs
        if line.strip():
            if in_list:
                latex_lines.append('\\end{itemize}')
                in_list = False

            text = escape_latex(line.strip())
            text = convert_inline_formatting(text)
            latex_lines.append(text)
        else:
            if not in_list:
                latex_lines.append('')

        i += 1

    # Close any open lists
    if in_list:
        latex_lines.append('\\end{itemize}')

    return '\n'.join(latex_lines)

def convert_table_to_latex(table_lines):
    """Convert markdown table to LaTeX booktabs table."""
    # Parse table
    rows = []
    for line in table_lines:
        if '---' in line:  # Skip separator line
            continue
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        rows.append(cells)

    if not rows:
        return ''

    # Determine column count
    num_cols = len(rows[0])
    col_spec = 'l' * num_cols

    # Build LaTeX table
    latex = ['\\begin{table}[htbp]']
    latex.append('\\centering')
    latex.append(f'\\begin{{tabular}}{{{col_spec}}}')
    latex.append('\\toprule')

    # Header row
    header = rows[0]
    header_escaped = [escape_latex(convert_inline_formatting(cell)) for cell in header]
    latex.append(' & '.join(header_escaped) + ' \\\\')
    latex.append('\\midrule')

    # Data rows
    for row in rows[1:]:
        row_escaped = [escape_latex(convert_inline_formatting(cell)) for cell in row]
        latex.append(' & '.join(row_escaped) + ' \\\\')

    latex.append('\\bottomrule')
    latex.append('\\end{tabular}')
    latex.append('\\caption{Table caption}')
    latex.append('\\label{tab:table}')
    latex.append('\\end{table}')

    return '\n'.join(latex)

def split_paper_into_sections(paper_path):
    """Split markdown paper into sections."""
    with open(paper_path, 'r') as f:
        content = f.read()

    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]

    # Split by level 1 headers
    sections = {}
    current_section = None
    current_content = []

    for line in content.split('\n'):
        if line.startswith('# '):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[2:].strip()
            current_content = []
        else:
            current_content.append(line)

    # Add last section
    if current_section:
        sections[current_section] = '\n'.join(current_content)

    return sections

def main():
    """Main conversion function."""
    paper_path = Path('06_paper_final.md')
    output_dir = Path('overleaf/sections')
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading paper from {paper_path}")
    sections = split_paper_into_sections(paper_path)

    # Section order for ICML
    section_order = [
        'Abstract',
        'Introduction',
        'Related Work',
        'Methodology',
        'Experiments',
        'Results',
        'Discussion',
        'Conclusion'
    ]

    section_files = {}

    for i, section_name in enumerate(section_order, 1):
        if section_name not in sections:
            print(f"Warning: Section '{section_name}' not found in paper")
            continue

        print(f"Converting section {i}: {section_name}")

        # Convert to LaTeX
        latex_content = convert_section_to_latex(section_name, sections[section_name])

        # Write to file
        filename = f'{i:02d}_{section_name.lower().replace(" ", "_")}.tex'
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            f.write(latex_content)

        section_files[section_name] = filename
        print(f"  → {filepath}")

    print(f"\nConverted {len(section_files)} sections to LaTeX")
    return section_files

if __name__ == '__main__':
    main()
