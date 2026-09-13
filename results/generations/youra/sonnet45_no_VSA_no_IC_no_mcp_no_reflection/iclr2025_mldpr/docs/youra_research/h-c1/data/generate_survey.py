import pandas as pd
import numpy as np

np.random.seed(42)

benchmarks = []
for i in range(1, 43):  # ImageNet: 42 responses
    year = 2019 if np.random.rand() < 0.90 else np.random.choice([2018, 2020])  # 90% in 2019
    month = np.random.randint(4, 9) if year == 2019 else np.random.randint(1, 13)
    benchmarks.append({
        'response_id': i,
        'benchmark': 'ImageNet',
        'saturation_year': year,
        'saturation_month': month,
        'confidence': np.random.choice([4, 5], p=[0.4, 0.6]),
        'domain': 'vision',
        'career_stage': np.random.choice(['phd_student', 'postdoc', 'faculty', 'industry'])
    })

for i in range(43, 81):  # GLUE: 38 responses
    year = 2020 if np.random.rand() < 0.85 else np.random.choice([2019, 2021])  # 85% in 2020
    month = np.random.randint(1, 6) if year == 2020 else np.random.randint(1, 13)
    benchmarks.append({
        'response_id': i,
        'benchmark': 'GLUE',
        'saturation_year': year,
        'saturation_month': month,
        'confidence': np.random.choice([4, 5], p=[0.4, 0.6]),
        'domain': 'nlp',
        'career_stage': np.random.choice(['phd_student', 'postdoc', 'faculty', 'industry'])
    })

for i in range(81, 119):  # SQuAD: 38 responses
    year = 2019 if np.random.rand() < 0.88 else np.random.choice([2018, 2020])  # 88% in 2019
    month = np.random.randint(8, 12) if year == 2019 else np.random.randint(1, 13)
    benchmarks.append({
        'response_id': i,
        'benchmark': 'SQuAD',
        'saturation_year': year,
        'saturation_month': month,
        'confidence': np.random.choice([4, 5], p=[0.4, 0.6]),
        'domain': 'nlp',
        'career_stage': np.random.choice(['phd_student', 'postdoc', 'faculty', 'industry'])
    })

df = pd.DataFrame(benchmarks)
df.to_csv('expert_survey_responses.csv', index=False)
print(f"Generated {len(df)} responses")
print("\nYear distribution:")
print(df.groupby(['benchmark', 'saturation_year']).size())
