import pandas as pd
import numpy as np
import re
from typing import Optional

VENUE_PATTERNS = {
    'NeurIPS': [r'neurips', r'nips', r'neural information processing'],
    'ICML': [r'icml', r'international conference on machine learning'],
    'ICLR': [r'iclr', r'international conference on learning representations']
}

VENUES = ["NeurIPS", "ICML", "ICLR"]
YEARS = list(range(2018, 2025))

# Real benchmark datasets commonly used in ML papers
BENCHMARK_DATASETS = [
    "ImageNet", "CIFAR-10", "CIFAR-100", "MNIST", "Fashion-MNIST",
    "COCO", "VOC", "ADE20K", "Cityscapes", "KITTI",
    "SQuAD", "GLUE", "SuperGLUE", "WMT", "CNN/DailyMail",
    "LibriSpeech", "VoxCeleb", "AudioSet", "ESC-50",
    "Atari", "MuJoCo", "OpenAI Gym", "DMControl",
    "ModelNet40", "ShapeNet", "ScanNet", "NYU-Depth",
    "Kinetics-400", "UCF-101", "HMDB-51", "Something-Something",
    "MS MARCO", "Natural Questions", "TriviaQA", "HotpotQA"
]

def normalize_venue(venue_str: str) -> Optional[str]:
    if not venue_str or pd.isna(venue_str):
        return None
    v_lower = str(venue_str).lower()
    for venue, patterns in VENUE_PATTERNS.items():
        for p in patterns:
            if re.search(p, v_lower):
                return venue
    return None

def extract_year(date_str) -> Optional[int]:
    if pd.isna(date_str):
        return None
    s = str(date_str)
    match = re.search(r'(20\d{2})', s)
    if match:
        y = int(match.group(1))
        if 2018 <= y <= 2024:
            return y
    return None

def load_pwc_data(cache_file: str = "pwc_papers_cache.parquet") -> pd.DataFrame:
    """Load real PWC data from HuggingFace datasets with caching."""
    import os
    from pathlib import Path
    from datasets import load_dataset

    cache_path = Path(__file__).parent / cache_file
    if cache_path.exists():
        print(f"Loading cached data from {cache_path}")
        return pd.read_parquet(cache_path)

    print("Loading PWC data from HuggingFace (first run, will cache)...")

    # Load papers with venue/date info
    papers_ds = load_dataset("pwc-archive/papers-with-abstracts", split="train")
    papers_df = papers_ds.to_pandas()
    print(f"Loaded {len(papers_df)} papers")

    # Vectorized venue/year extraction
    papers_df['venue_norm'] = papers_df['proceeding'].fillna(papers_df['conference']).fillna('')
    papers_df['venue'] = papers_df['venue_norm'].apply(normalize_venue)
    papers_df['year'] = papers_df['date'].apply(extract_year)

    # Filter to valid NeurIPS/ICML/ICLR 2018-2024
    valid = papers_df.dropna(subset=['paper_url', 'venue', 'year'])
    valid = valid[valid['venue'].isin(VENUES) & valid['year'].isin(YEARS)]
    paper_info = valid.set_index('paper_url')[['venue', 'year']].to_dict('index')
    print(f"Found {len(paper_info)} papers with valid venue/year (NeurIPS/ICML/ICLR 2018-2024)")

    # Use tasks column as proxy for "what benchmarks this paper evaluates on"
    # tasks like "Image Classification", "Object Detection" indicate benchmark categories
    valid_with_tasks = valid[valid['tasks'].apply(lambda x: len(x) > 0)]

    # Build DataFrame: paper -> tasks (as datasets proxy)
    papers = []
    for _, row in valid_with_tasks.iterrows():
        tasks = list(row['tasks'])  # Convert numpy array to list
        if tasks:
            papers.append({
                'paper_id': row['paper_url'],
                'venue': row['venue'],
                'year': int(row['year']),
                'datasets': tasks  # Using tasks as benchmark/dataset proxy
            })

    df = pd.DataFrame(papers)
    print(f"Created {len(df)} papers with task labels (as dataset proxy)")

    # Cache for next run
    df.to_parquet(cache_path)
    print(f"Cached to {cache_path}")

    venue_year_counts = df.groupby(['venue', 'year']).size()
    print(f"Venue-year coverage: {len(venue_year_counts)}/21")

    return df
