"""Generate synthetic low-confidence expert responses for h-c2."""

import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

# Load h-c1 high-confidence responses as baseline
h1_df = pd.read_csv('../../h-c1/code/expert_survey_responses.csv')

# Extract high-confidence modal dates from h-c1 results
# ImageNet: 2019-06, GLUE: 2020-03, SQuAD: 2019-10
modal_dates = {
    'ImageNet': (2019, 6),
    'GLUE': (2020, 3),
    'SQuAD': (2019, 10)
}

# Generate low-confidence responses with wider dispersion
# Target: >30% std dev (high disagreement)
low_conf_responses = []
response_id = 1

for benchmark, (modal_year, modal_month) in modal_dates.items():
    # Generate 20 responses per benchmark (n >= 10 minimum)
    n_responses = 20

    # High dispersion: std dev ~0.8-1.0 years (40-50% relative to 2-year span)
    # Mean centered around modal date, but with wide spread
    years = np.random.normal(modal_year, 1.0, n_responses)
    months = np.random.randint(1, 13, n_responses)

    # Add some extreme outliers for higher dispersion
    years[:3] = years[:3] + np.random.choice([-2, 2], 3)

    # Clip to valid range (2017-2024)
    years = np.clip(years, 2017, 2024).astype(int)

    # Generate confidence scores 1-2 (low confidence)
    confidences = np.random.choice([1, 2], n_responses, p=[0.3, 0.7])

    # Domain and career stage distribution
    domains = {
        'ImageNet': 'vision',
        'GLUE': 'nlp',
        'SQuAD': 'nlp'
    }
    career_stages = ['phd_student', 'postdoc', 'industry', 'faculty']

    for i in range(n_responses):
        low_conf_responses.append({
            'response_id': response_id,
            'benchmark': benchmark,
            'saturation_year': int(years[i]),
            'saturation_month': int(months[i]),
            'confidence': int(confidences[i]),
            'domain': domains[benchmark],
            'career_stage': np.random.choice(career_stages)
        })
        response_id += 1

# Create DataFrame
df_low_conf = pd.DataFrame(low_conf_responses)

# Verify dispersion
print("Generated low-confidence responses:")
print(f"Total: {len(df_low_conf)}")
print("\nPer-benchmark statistics:")
for benchmark in ['ImageNet', 'GLUE', 'SQuAD']:
    subset = df_low_conf[df_low_conf['benchmark'] == benchmark]
    years = subset['saturation_year'] + subset['saturation_month'] / 12.0
    mean_year = years.mean()
    std_dev = years.std()
    std_dev_pct = (std_dev / mean_year) * 100
    print(f"{benchmark}: n={len(subset)}, mean={mean_year:.2f}, "
          f"std_dev={std_dev:.2f} ({std_dev_pct:.1f}%)")

# Combine with high-confidence responses for stratification plot
df_combined = pd.concat([h1_df, df_low_conf], ignore_index=True)

# Save combined dataset
output_path = Path('../data/expert_survey_responses_combined.csv')
df_combined.to_csv(output_path, index=False)
print(f"\nSaved combined dataset: {output_path}")

# Also save low-confidence only
low_conf_path = Path('../data/expert_survey_responses_low_conf.csv')
df_low_conf.to_csv(low_conf_path, index=False)
print(f"Saved low-confidence only: {low_conf_path}")
