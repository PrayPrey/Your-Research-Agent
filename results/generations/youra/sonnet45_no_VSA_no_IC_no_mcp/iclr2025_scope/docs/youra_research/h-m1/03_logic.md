# Logic Specification: H-M1

**Date:** 2026-08-25  
**Hypothesis:** Feature Extraction Protocol Inter-Rater Agreement  
**Type:** MECHANISM (Annotation Study)  
**Budget:** 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Existing patterns found - reusing bcvf evaluation modules for sklearn metrics integration  
**Analyzed Path:** `src/bcvf/`  
**Relevant Symbols:**
- `BCVFValidator` class - sklearn metrics pattern (precision/recall/f1)
- `ProvenanceExtractor.extract()` - keyword-based scoring pattern
- Pattern: metrics dict + gate decision logic

---

## M1-2: Feature Extraction Protocol [Complexity: 12, Budget: 1]

**Applied:** Keyword-based extraction pattern from bcvf/extractors/provenance_extractor.py

### API Signatures

```python
from typing import List, Dict

class FeatureExtractor:
    """Extract features from benchmark papers using standardized protocol."""
    
    def __init__(self, taxonomy_path: str, metrics_config: str):
        """Load PWC taxonomy and metrics regex patterns."""
        self.taxonomy = self._load_json(taxonomy_path)  # dict
        self.metric_patterns = self._load_json(metrics_config)  # dict[metric_name, regex]
    
    def extract_task_type(self, abstract: str, title: str) -> str:
        """Map to PWC taxonomy. Returns: taxonomy category string."""
        ...
    
    def extract_metrics(self, full_text: str) -> List[str]:
        """Regex-based metric extraction. Returns: list of metric names."""
        ...
    
    def extract_modality(self, description: str) -> str:
        """Decision tree classification. Returns: image|text|audio|video|multimodal."""
        ...
    
    def extract_dataset_size(self, tables: List[str]) -> int:
        """Parse table text for sample count. Returns: total dataset size."""
        ...
    
    def extract_all(self, paper: dict) -> dict:
        """Extract all features. paper: {title, abstract, full_text, tables}. Returns: feature dict."""
        ...
```

### Tensor Shapes

N/A (text processing, no tensors)

### Pseudo-code

```
extract_task_type:
1. keywords = abstract + title (lowercased)
2. for category in taxonomy:
     score = sum(1 for term in taxonomy[category] if term in keywords)
3. return category with max score

extract_metrics:
1. matches = []
2. for metric_name, pattern in metric_patterns.items():
     if re.search(pattern, full_text, re.IGNORECASE):
       matches.append(metric_name)
3. return matches

extract_modality:
1. if 'image' or 'vision' in description: return 'image'
2. if 'text' or 'language' in description: return 'text'
3. if 'audio' or 'speech' in description: return 'audio'
4. if 'video' in description: return 'video'
5. if multiple modalities found: return 'multimodal'

extract_dataset_size:
1. numbers = re.findall(r'\d{1,3}(?:,\d{3})*', tables)
2. candidates = [int(n.replace(',', '')) for n in numbers if int(n) > 100]
3. return max(candidates) if candidates else 0
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Taxonomy mapper + regex engine | PWC taxonomy lookup, regex pattern matching for metrics |

---

## M1-3: Agreement Calculation [Complexity: 10, Budget: 1]

**Applied:** sklearn.metrics integration pattern from bcvf/evaluation/validator.py

### API Signatures

```python
import numpy as np
from sklearn.metrics import cohen_kappa_score
from scipy.stats import pearsonr
from typing import List, Tuple, Dict
import pandas as pd

class AgreementCalculator:
    """Calculate inter-rater agreement metrics."""
    
    def calculate_kappa(self, labels1: List[str], labels2: List[str]) -> float:
        """Cohen's kappa for categorical features. Returns: kappa score [-1, 1]."""
        return cohen_kappa_score(labels1, labels2)
    
    def calculate_icc(self, ratings: np.ndarray) -> float:
        """ICC for continuous features. ratings: [n_samples, 2]. Returns: ICC score [0, 1]."""
        ...
    
    def compute_confidence_interval(self, kappa: float, n: int) -> Tuple[float, float]:
        """95% CI via bootstrap. Returns: (lower, upper)."""
        ...
    
    def analyze_disagreements(
        self, 
        labels1: List[str], 
        labels2: List[str],
        benchmark_ids: List[str]
    ) -> pd.DataFrame:
        """Identify disagreement patterns. Returns: df with benchmark_id, label1, label2."""
        ...
```

### Pseudo-code

```
calculate_icc(ratings):
1. n, k = ratings.shape  # n samples, k=2 raters
2. mean_ratings = mean(ratings, axis=1)  # [n]
3. ss_between = k * sum((mean_ratings - global_mean)^2)
4. ss_within = sum((ratings - mean_ratings[:, None])^2)
5. ms_between = ss_between / (n - 1)
6. ms_within = ss_within / (n * (k - 1))
7. icc = (ms_between - ms_within) / (ms_between + (k - 1) * ms_within)

compute_confidence_interval(kappa, n):
1. # Bootstrap: 1000 resamples
2. for i in 1..1000:
     indices = random.choice(range(n), size=n, replace=True)
     kappa_boot[i] = cohen_kappa(labels1[indices], labels2[indices])
3. return (percentile(kappa_boot, 2.5), percentile(kappa_boot, 97.5))

analyze_disagreements(labels1, labels2, benchmark_ids):
1. disagreements = [(id, l1, l2) for id, l1, l2 in zip(benchmark_ids, labels1, labels2) if l1 != l2]
2. return DataFrame(disagreements, columns=['benchmark_id', 'annotator1', 'annotator2'])
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Kappa + ICC calculation | sklearn cohen_kappa_score, scipy ICC formula, bootstrap CI |

---

## M1-4: Annotation Workflow [Complexity: 9, Budget: 1]

**Applied:** Standard workflow orchestration pattern

### API Signatures

```python
import pandas as pd
from typing import List, Dict

class AnnotationWorkflow:
    """Orchestrate annotation process with calibration and versioning."""
    
    def __init__(self, protocol_version: str, extractor: FeatureExtractor):
        """Initialize workflow with protocol version and extractor instance."""
        self.protocol_version = protocol_version
        self.extractor = extractor
    
    def calibrate(self, practice_benchmarks: List[dict]) -> Dict[str, float]:
        """Pre-study calibration on 3 practice samples. Returns: initial kappa scores."""
        ...
    
    def annotate(
        self, 
        benchmarks: List[dict], 
        annotator_id: str
    ) -> pd.DataFrame:
        """Independent annotation. benchmarks: list of paper dicts. Returns: df with features."""
        ...
    
    def save_annotations(self, annotations: pd.DataFrame, output_path: str) -> None:
        """Save with timestamp and protocol version."""
        ...
```

### Pseudo-code

```
calibrate(practice_benchmarks):
1. a1_features = [extractor.extract_all(b) for b in practice_benchmarks[:3]]
2. a2_features = [extractor.extract_all(b) for b in practice_benchmarks[:3]]
3. kappa = cohen_kappa([f['task_type'] for f in a1_features], [f['task_type'] for f in a2_features])
4. return {'calibration_kappa': kappa}

annotate(benchmarks, annotator_id):
1. rows = []
2. for b in benchmarks:
     features = extractor.extract_all(b)
     features['benchmark_id'] = b['id']
     features['annotator_id'] = annotator_id
     features['timestamp'] = now()
     rows.append(features)
3. return DataFrame(rows)

save_annotations(annotations, output_path):
1. annotations['protocol_version'] = self.protocol_version
2. annotations.to_csv(output_path, index=False)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Workflow orchestration | Calibration procedure, annotation tracking, CSV export |

---

## M1-1: Benchmark Sampling [Complexity: 8, Budget: 1]

**Applied:** Standard API client pattern with stratified sampling

### API Signatures

```python
import requests
import pandas as pd
from typing import List

class BenchmarkSampler:
    """Sample benchmarks from Papers with Code API."""
    
    def __init__(self, api_url: str = "https://paperswithcode.com/api/v1/datasets/"):
        """Initialize API client."""
        self.api_url = api_url
    
    def sample_stratified(
        self, 
        n_samples: int = 20, 
        seed: int = 42
    ) -> pd.DataFrame:
        """Stratified sampling by task type and modality. Returns: df with benchmark metadata."""
        ...
    
    def verify_accessibility(self, benchmarks: pd.DataFrame) -> pd.DataFrame:
        """Check if papers are accessible. Returns: df with 'accessible' column."""
        ...
```

### Pseudo-code

```
sample_stratified(n_samples, seed):
1. response = requests.get(api_url)
2. all_benchmarks = response.json()['results']
3. # Stratify by task type
4. vision = [b for b in all_benchmarks if 'vision' in b['task']]
5. language = [b for b in all_benchmarks if 'language' in b['task']]
6. audio = [b for b in all_benchmarks if 'audio' in b['task']]
7. multimodal = [b for b in all_benchmarks if 'multimodal' in b['task']]
8. # Sample with seed
9. random.seed(seed)
10. selected = random.sample(vision, 8) + random.sample(language, 7) + random.sample(audio, 3) + random.sample(multimodal, 2)
11. return DataFrame(selected)

verify_accessibility(benchmarks):
1. for idx, row in benchmarks.iterrows():
     paper_url = row['paper_url']
     accessible = requests.head(paper_url).status_code == 200
     benchmarks.loc[idx, 'accessible'] = accessible
2. return benchmarks
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | API sampling + verification | requests.get(), stratified sampling, accessibility check |

---

## External Dependencies

**No base hypothesis.** Green-field implementation using existing codebase patterns only.

**Existing Codebase APIs (Reused Patterns):**

From `src/bcvf/evaluation/validator.py`:
```python
# Pattern: sklearn metrics + gate decision
from sklearn.metrics import cohen_kappa_score
metrics = {
    'precision': precision_score(y_true, y_pred),
    'recall': recall_score(y_true, y_pred),
    'f1': f1_score(y_true, y_pred)
}
gate_decision = 'PASS' if all(m >= threshold for m in metrics.values()) else 'FAIL'
```

From `src/bcvf/extractors/provenance_extractor.py`:
```python
# Pattern: keyword-based scoring
keywords = ['keyword1', 'keyword2', ...]
count = sum(1 for kw in keywords if kw in text.lower())
score = count / len(keywords)
return {'score': score, 'confidence': confidence}
```

---

## Remaining Tasks (Not in Logic Spec)

**M1-5: Evaluation & Gate Logic** (Complexity: 7) - Trivial wrapper around AgreementCalculator
**M1-6: Visualization** (Complexity: 8) - Standard matplotlib/seaborn boilerplate
**M1-7: Configuration & Data** (Complexity: 6) - Dataclass + JSON files (no logic)

These are implementation-ready from architecture spec alone. No API design needed.

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes skipped (text processing, no tensors)
- [x] Subtask count within budget (4/4 used)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field project noted (no base hypothesis)
- [x] Existing codebase patterns documented
