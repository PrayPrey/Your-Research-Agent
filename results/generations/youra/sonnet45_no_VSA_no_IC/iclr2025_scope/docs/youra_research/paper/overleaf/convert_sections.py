#!/usr/bin/env python3
"""Convert Markdown sections to LaTeX"""
import re

def escape_latex(text):
    """Escape special LaTeX characters"""
    # Don't escape in math mode
    parts = re.split(r'(\$\$?.*?\$\$?)', text)
    escaped = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # Math mode
            escaped.append(part)
        else:  # Normal text
            part = part.replace('\\', '\\textbackslash{}')
            part = part.replace('%', '\\%')
            part = part.replace('&', '\\&')
            part = part.replace('#', '\\#')
            part = part.replace('_', '\\_')
            part = part.replace('{', '\\{')
            part = part.replace('}', '\\}')
            part = part.replace('~', '\\textasciitilde{}')
            part = part.replace('^', '\\^{}')
            escaped.append(part)
    return ''.join(escaped)

def convert_section(md_text, section_title):
    """Convert Markdown section to LaTeX"""
    latex = []

    # Add section header (skip for abstract)
    if section_title.lower() != 'abstract':
        latex.append(f'\\section{{{section_title}}}\n')

    # Split into paragraphs
    paragraphs = md_text.strip().split('\n\n')

    for para in paragraphs:
        if not para.strip():
            continue

        # Headers
        if para.startswith('###'):
            title = para.replace('###', '').strip()
            latex.append(f'\\subsubsection{{{title}}}\n')
        elif para.startswith('##'):
            title = para.replace('##', '').strip()
            latex.append(f'\\subsection{{{title}}}\n')
        elif para.startswith('#'):
            continue  # Skip main section headers

        # Lists
        elif para.strip().startswith('-') or re.match(r'^\d+\.', para.strip()):
            if para.strip().startswith('-'):
                latex.append('\\begin{itemize}\n')
                for line in para.split('\n'):
                    if line.strip().startswith('-'):
                        item = line.strip()[1:].strip()
                        item = convert_inline(item)
                        latex.append(f'\\item {item}\n')
                latex.append('\\end{itemize}\n')
            else:
                latex.append('\\begin{enumerate}\n')
                for line in para.split('\n'):
                    if re.match(r'^\d+\.', line.strip()):
                        item = re.sub(r'^\d+\.\s*', '', line.strip())
                        item = convert_inline(item)
                        latex.append(f'\\item {item}\n')
                latex.append('\\end{enumerate}\n')

        # Regular paragraphs
        else:
            converted = convert_inline(para)
            latex.append(f'{converted}\n\n')

    return ''.join(latex)

def convert_inline(text):
    """Convert inline Markdown to LaTeX"""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)

    # Italic
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)

    # Code
    text = re.sub(r'`(.+?)`', r'\\texttt{\1}', text)

    # Citations [Author, Year]
    text = re.sub(r'\[([A-Z][a-zA-Z]+ et al\., \d{4})\]', r'\\cite{\1}', text)
    text = re.sub(r'\[([A-Z][a-zA-Z]+ & [A-Z][a-zA-Z]+, \d{4})\]', r'\\cite{\1}', text)

    return text

# Read paper
with open('../06_paper_final.md', 'r') as f:
    content = f.read()

# Split sections
sections = {
    'introduction': ('Introduction', '# Introduction', '# Related Work'),
    'related_work': ('Related Work', '# Related Work', '# Methodology'),
    'methodology': ('Methodology', '# Methodology', '# Experiments'),
    'experiments': ('Experimental Setup', '# Experiments', '# Results'),
    'results': ('Results', '# Results', '# Discussion'),
    'discussion': ('Discussion', '# Discussion', '# Conclusion'),
    'conclusion': ('Conclusion', '# Conclusion', None),
}

for filename, (title, start, end) in sections.items():
    start_idx = content.find(start)
    if end:
        end_idx = content.find(end)
        section_text = content[start_idx:end_idx]
    else:
        section_text = content[start_idx:]

    # Remove header
    section_text = section_text.replace(start, '', 1).strip()

    # Convert
    latex_content = convert_section(section_text, title)

    # Write
    with open(f'sections/{filename}.tex', 'w') as f:
        f.write(latex_content)

    print(f'✓ {filename}.tex')

print('All sections converted')
