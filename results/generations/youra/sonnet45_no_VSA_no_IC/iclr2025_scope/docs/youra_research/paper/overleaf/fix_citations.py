import re

# Citation map: (Author, Year) -> BibTeX key
citations = {
    ('Zhang et al.', '2023'): 'zhang2023h2o',
    ('Zhang et al.', '2024'): 'zhang2023h2o',  # alias (paper uses 2024)
    ('Xiao et al.', '2024'): 'xiao2024streamingllm',
    ('Liu et al.', '2024'): 'liu2024dynamickv',
    ('Karpukhin et al.', '2020'): 'karpukhin2020dpr',
    ('Izacard et al.', '2021'): 'izacard2022contriever',
    ('Carbonell & Goldstein', '1998'): 'carbonell1998mmr',
    ('Clarke et al.', '2008'): 'clarke2008novelty',
    ('Yang et al.', '2018'): 'yang2018hotpotqa',
    ('Trivedi et al.', '2022'): 'trivedi2022musique',
    ('Touvron et al.', '2023'): 'touvron2023llama2',
}

import os
os.chdir('sections')

for filename in ['introduction.tex', 'related_work.tex', 'methodology.tex', 'experiments.tex']:
    with open(filename, 'r') as f:
        content = f.read()
    
    for (author, year), key in citations.items():
        # Match patterns like (Author, Year) or Author (Year)
        patterns = [
            rf'\({re.escape(author)}, {year}\)',
            rf'{re.escape(author)} \({year}\)',
        ]
        for pattern in patterns:
            content = re.sub(pattern, rf'\\cite{{{key}}}', content)
    
    with open(filename, 'w') as f:
        f.write(content)

print("Citations fixed in 4 section files")
