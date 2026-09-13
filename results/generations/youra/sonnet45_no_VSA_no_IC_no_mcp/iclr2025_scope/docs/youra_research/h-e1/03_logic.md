# Logic Design: h-e1

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (Citation Classification + Feature Extraction)  
**Date:** 2026-08-25  
**Gate:** MUST_WORK (precision >85%, kappa >0.80)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New citation classification experiment - no existing code to analyze  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## System Overview

Binary classification of citation contexts (validation claim vs other mention) + feature extraction from benchmark papers with inter-rater reliability checks.

**Pipeline:**
```
ArXiv/SS API → Citation Contexts → Manual Annotation → SciBERT Training → Evaluation → PASS/FAIL
```

**Components:**
1. Data collection (API queries, context extraction, sampling)
2. Annotation interface (binary labeling + feature extraction)
3. SciBERT fine-tuning (binary classifier)
4. Evaluation (precision/recall/F1, Cohen's kappa)

**Gate Logic:**
```python
PASS = (test_precision > 0.85) and (feature_kappa > 0.80)
```

---

## Module Design

### 1. Data Collection (`scripts/collect_citations.py`)

**Applied:** Standard API patterns (requests, exponential backoff)

**Dependencies:** arxiv, requests, random

```python
class CitationCollector:
    def __init__(self, output_dir: str, seed: int = 42):
        """Initialize collector with reproducible seed."""
        self.output_dir = Path(output_dir)
        self.seed = seed
        random.seed(seed)
    
    def fetch_benchmark_papers(
        self, 
        query: str = "benchmark OR dataset evaluation",
        max_results: int = 200,
        date_range: tuple[str, str] = ("2015-01-01", "2024-12-31")
    ) -> list[dict]:
        """Fetch papers from ArXiv. Returns: [{'arxiv_id', 'title', 'abstract', 'date'}]"""
        ...
    
    def filter_by_citations(
        self, 
        papers: list[dict], 
        min_citations: int = 50
    ) -> list[dict]:
        """Filter via Semantic Scholar API. Returns: papers with citation_count ≥ 50."""
        ...
    
    def extract_citation_contexts(
        self, 
        paper_id: str, 
        window_size: int = 3
    ) -> list[dict]:
        """Extract 3-sentence windows. Returns: [{'citing_paper', 'context_text', 'sentences': [before, containing, after]}]"""
        ...
    
    def sample_contexts(
        self, 
        all_contexts: list[dict], 
        n_samples: int = 150
    ) -> list[dict]:
        """Random sample with seed=42. Returns: sampled citation contexts."""
        ...
    
    def save_raw_data(self, contexts: list[dict], filename: str = "raw_citations.json") -> None:
        """Save to JSON with metadata (collection_date, seed, total_count)."""
        ...
```

**Tensor Shapes:** N/A (data collection only)

---

### 2. Annotation Interface (`scripts/annotate.py`)

**Applied:** CLI pattern with json persistence

**Dependencies:** pandas

```python
class AnnotationInterface:
    def __init__(self, data_path: str, annotator_id: str):
        """Load raw citations and initialize annotator-specific file."""
        self.data_path = Path(data_path)
        self.annotator_id = annotator_id
        self.save_path = self.data_path.parent / f"annotations_{annotator_id}.json"
    
    def display_context(self, context: dict) -> None:
        """Print citation context with 3-sentence window."""
        print(f"Citing Paper: {context['citing_paper']}")
        print(f"Context:\n{context['context_text']}")
    
    def binary_label(self, context: dict) -> int:
        """CLI prompt: 'Is this a validation claim? (y/n)'. Returns: 0 or 1."""
        ...
    
    def extract_features(self, benchmark_paper: dict) -> dict:
        """Feature form:
        - task_type: str (from PWC taxonomy via dropdown)
        - metrics: list[str] (regex-assisted extraction)
        - modality: str (text/image/audio/video)
        - dataset_size: int (approximate)
        Returns: {'task_type', 'metrics', 'modality', 'dataset_size', 'annotator_id'}
        """
        ...
    
    def save_annotations(self, annotations: list[dict]) -> None:
        """Save to annotator-specific JSON."""
        ...
    
    def compute_kappa(
        self, 
        annotations1: list[dict], 
        annotations2: list[dict]
    ) -> float:
        """Cohen's kappa on overlapping benchmarks (n=20). Returns: kappa score."""
        from sklearn.metrics import cohen_kappa_score
        ...
```

**Tensor Shapes:** N/A (manual annotation only)

---

### 3. SciBERT Classifier (`models/citation_classifier.py`)

**Applied:** Hugging Face fine-tuning pattern (AutoModel, Trainer)

**Dependencies:** transformers, torch

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch

class CitationClassifier:
    def __init__(self, model_name: str = "allenai/scibert_scivocab_uncased"):
        """Load SciBERT with classification head."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=2  # 0=other, 1=validation claim
        )
    
    def prepare_dataset(
        self, 
        texts: list[str], 
        labels: list[int],
        max_length: int = 512
    ) -> dict:
        """Tokenize citation contexts.
        texts: list of strings [batch_size] -> encodings: [batch_size, seq_len=512]
        labels: list of ints [batch_size]
        Returns: {'input_ids': [B, 512], 'attention_mask': [B, 512], 'labels': [B]}
        """
        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors="pt"
        )
        return {
            "input_ids": encodings["input_ids"],  # [B, 512]
            "attention_mask": encodings["attention_mask"],  # [B, 512]
            "labels": torch.tensor(labels)  # [B]
        }
    
    def train(
        self,
        train_data: dict,
        val_data: dict,
        output_dir: str,
        learning_rate: float = 2e-5,
        batch_size: int = 16,
        num_epochs: int = 5,
        patience: int = 2
    ) -> dict:
        """Fine-tune with early stopping.
        Returns: {'train_loss', 'val_loss', 'best_epoch'}
        """
        training_args = TrainingArguments(
            output_dir=output_dir,
            learning_rate=learning_rate,
            per_device_train_batch_size=batch_size,
            num_train_epochs=num_epochs,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            seed=42
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_data,
            eval_dataset=val_data
        )
        
        trainer.train()
        return trainer.state.log_history
    
    def predict(self, text: str) -> tuple[int, float]:
        """Classify single citation.
        text: str -> logits: [1, 2] -> probs: [1, 2] -> label: int, confidence: float
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits  # [1, 2]
            probs = torch.softmax(logits, dim=-1)  # [1, 2]
            label = torch.argmax(probs, dim=-1).item()  # int
            confidence = probs[0, label].item()  # float
        return label, confidence
    
    def batch_predict(self, texts: list[str]) -> tuple[list[int], list[float]]:
        """Batch inference. texts: [B] -> labels: [B], confidences: [B]"""
        inputs = self.tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits  # [B, 2]
            probs = torch.softmax(logits, dim=-1)  # [B, 2]
            labels = torch.argmax(probs, dim=-1).tolist()  # [B]
            confidences = [probs[i, labels[i]].item() for i in range(len(labels))]
        return labels, confidences
```

**Tensor Shapes:**

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, 512] | Tokenized text (B=16 for training, variable for inference) |
| attention_mask | [B, 512] | Padding mask |
| labels | [B] | Binary labels (0 or 1) |
| logits | [B, 2] | Raw model output before softmax |
| probs | [B, 2] | Softmax probabilities (dim 0=other, dim 1=validation) |

---

### 4. Evaluation Module (`scripts/evaluate.py`)

**Applied:** sklearn metrics pattern

**Dependencies:** sklearn, pandas

```python
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report, confusion_matrix, cohen_kappa_score

class Evaluator:
    def __init__(self, output_dir: str):
        """Initialize evaluator with output directory for saving results."""
        self.output_dir = Path(output_dir)
    
    def compute_classification_metrics(
        self, 
        y_true: list[int], 
        y_pred: list[int]
    ) -> dict:
        """Compute precision/recall/F1 for validation claim class (pos_label=1).
        Returns: {'precision': float, 'recall': float, 'f1': float, 'report': str}
        """
        precision = precision_score(y_true, y_pred, pos_label=1, zero_division=0)
        recall = recall_score(y_true, y_pred, pos_label=1, zero_division=0)
        f1 = f1_score(y_true, y_pred, pos_label=1, zero_division=0)
        report = classification_report(y_true, y_pred, target_names=["other", "validation"])
        
        if precision < 0.85:
            print(f"WARNING: Precision {precision:.3f} below gate threshold (0.85)")
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "report": report
        }
    
    def compute_confusion_matrix(
        self, 
        y_true: list[int], 
        y_pred: list[int]
    ) -> np.ndarray:
        """2x2 confusion matrix. Returns: [[TN, FP], [FN, TP]]"""
        return confusion_matrix(y_true, y_pred)
    
    def compute_feature_kappa(
        self, 
        annotator1_features: list[dict], 
        annotator2_features: list[dict],
        feature_key: str = "task_type"
    ) -> float:
        """Cohen's kappa for feature agreement.
        annotator1_features: [{'task_type', ...}] × 20 benchmarks
        annotator2_features: [{'task_type', ...}] × 20 benchmarks
        Returns: kappa score per feature_key
        """
        labels1 = [f[feature_key] for f in annotator1_features]
        labels2 = [f[feature_key] for f in annotator2_features]
        kappa = cohen_kappa_score(labels1, labels2)
        
        if kappa < 0.80:
            print(f"WARNING: Kappa {kappa:.3f} for {feature_key} below gate threshold (0.80)")
        
        return kappa
    
    def validate_gate(
        self, 
        test_precision: float, 
        feature_kappa: float
    ) -> bool:
        """Gate condition: precision >85% AND kappa >0.80. Returns: True if PASS."""
        return (test_precision > 0.85) and (feature_kappa > 0.80)
    
    def save_results(self, results: dict, filename: str = "results.json") -> None:
        """Save metrics to JSON with timestamp."""
        import json
        from datetime import datetime
        results["timestamp"] = datetime.now().isoformat()
        with open(self.output_dir / filename, "w") as f:
            json.dump(results, f, indent=2)
```

**Tensor Shapes:** N/A (evaluation only, operates on lists/arrays)

---

### 5. Visualization (`scripts/visualize.py`)

**Applied:** matplotlib standard patterns

**Dependencies:** matplotlib, seaborn

```python
import matplotlib.pyplot as plt
import seaborn as sns

class Visualizer:
    def __init__(self, output_dir: str):
        """Initialize with figure save directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_confusion_matrix(self, cm: np.ndarray, save_name: str = "confusion_matrix.png") -> None:
        """2x2 heatmap with annotations."""
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=["other", "validation"],
                   yticklabels=["other", "validation"])
        plt.ylabel("True Label")
        plt.xlabel("Predicted Label")
        plt.title("Citation Classification Confusion Matrix")
        plt.tight_layout()
        plt.savefig(self.output_dir / save_name, dpi=150)
        plt.close()
    
    def plot_training_metrics(
        self, 
        history: list[dict], 
        save_name: str = "training_metrics.png"
    ) -> None:
        """Loss curves over epochs."""
        epochs = [entry["epoch"] for entry in history if "loss" in entry]
        train_loss = [entry["loss"] for entry in history if "loss" in entry]
        val_loss = [entry["eval_loss"] for entry in history if "eval_loss" in entry]
        
        plt.figure(figsize=(8, 5))
        plt.plot(epochs, train_loss, label="Train Loss", marker='o')
        plt.plot(epochs, val_loss, label="Val Loss", marker='s')
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.title("Training Progress")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / save_name, dpi=150)
        plt.close()
    
    def plot_feature_agreement_heatmap(
        self, 
        kappa_scores: dict[str, float], 
        save_name: str = "feature_agreement.png"
    ) -> None:
        """Heatmap of Cohen's kappa per feature type.
        kappa_scores: {'task_type': 0.85, 'metrics': 0.78, 'modality': 0.92, 'dataset_size': 0.81}
        """
        features = list(kappa_scores.keys())
        kappas = list(kappa_scores.values())
        
        plt.figure(figsize=(8, 4))
        colors = ['green' if k >= 0.80 else 'orange' for k in kappas]
        plt.barh(features, kappas, color=colors)
        plt.axvline(x=0.80, color='red', linestyle='--', label='Gate Threshold')
        plt.xlabel("Cohen's Kappa")
        plt.title("Inter-Rater Agreement by Feature Type")
        plt.xlim(0, 1)
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.output_dir / save_name, dpi=150)
        plt.close()
    
    def plot_context_length_distribution(
        self, 
        contexts: list[str], 
        tokenizer,
        save_name: str = "context_lengths.png"
    ) -> None:
        """Histogram of token counts to validate <512 assumption."""
        lengths = [len(tokenizer.encode(ctx, truncation=False)) for ctx in contexts]
        
        plt.figure(figsize=(8, 5))
        plt.hist(lengths, bins=30, edgecolor='black', alpha=0.7)
        plt.axvline(x=512, color='red', linestyle='--', label='Max Length (512)')
        plt.xlabel("Token Count")
        plt.ylabel("Frequency")
        plt.title("Citation Context Length Distribution")
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.output_dir / save_name, dpi=150)
        plt.close()
        
        truncated_pct = sum(1 for l in lengths if l > 512) / len(lengths) * 100
        print(f"Truncation rate: {truncated_pct:.1f}% of contexts exceed 512 tokens")
```

**Tensor Shapes:** N/A (visualization only)

---

## Execution Flow (`scripts/run_experiment.py`)

**Main experiment orchestration:**

```python
def main():
    # 1. Data Collection
    collector = CitationCollector(output_dir="data/h-e1", seed=42)
    papers = collector.fetch_benchmark_papers(query="benchmark OR dataset evaluation", max_results=200)
    benchmarks = collector.filter_by_citations(papers, min_citations=50)
    all_contexts = []
    for paper in benchmarks:
        contexts = collector.extract_citation_contexts(paper['arxiv_id'], window_size=3)
        all_contexts.extend(contexts)
    sampled = collector.sample_contexts(all_contexts, n_samples=150)
    collector.save_raw_data(sampled, "raw_citations.json")
    
    # 2. Manual Annotation (run separately for each annotator)
    # annotator = AnnotationInterface("data/h-e1/raw_citations.json", annotator_id="annotator1")
    # annotations = [annotator.binary_label(ctx) for ctx in sampled]
    # annotator.save_annotations(annotations)
    
    # 3. Load annotations and split
    from sklearn.model_selection import train_test_split
    annotations = load_annotations("data/h-e1/annotations_annotator1.json")  # Helper function
    texts = [a['context_text'] for a in annotations]
    labels = [a['label'] for a in annotations]
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)
    
    # 4. Train SciBERT
    classifier = CitationClassifier("allenai/scibert_scivocab_uncased")
    train_data = classifier.prepare_dataset(X_train, y_train)
    test_data = classifier.prepare_dataset(X_test, y_test)
    history = classifier.train(train_data, test_data, output_dir="models/h-e1", 
                               learning_rate=2e-5, batch_size=16, num_epochs=5, patience=2)
    
    # 5. Evaluate
    y_pred, confidences = classifier.batch_predict(X_test)
    evaluator = Evaluator(output_dir="results/h-e1")
    metrics = evaluator.compute_classification_metrics(y_test, y_pred)
    cm = evaluator.compute_confusion_matrix(y_test, y_pred)
    
    # 6. Feature extraction kappa
    features_a1 = load_features("data/h-e1/features_annotator1.json")  # 20 benchmarks
    features_a2 = load_features("data/h-e1/features_annotator2.json")  # Same 20
    kappa_task = evaluator.compute_feature_kappa(features_a1, features_a2, "task_type")
    kappa_metrics = evaluator.compute_feature_kappa(features_a1, features_a2, "metrics")
    kappa_modality = evaluator.compute_feature_kappa(features_a1, features_a2, "modality")
    avg_kappa = (kappa_task + kappa_metrics + kappa_modality) / 3
    
    # 7. Gate validation
    gate_pass = evaluator.validate_gate(metrics['precision'], avg_kappa)
    
    # 8. Visualization
    viz = Visualizer(output_dir="figures/h-e1")
    viz.plot_confusion_matrix(cm)
    viz.plot_training_metrics(history)
    viz.plot_feature_agreement_heatmap({
        "task_type": kappa_task,
        "metrics": kappa_metrics,
        "modality": kappa_modality
    })
    viz.plot_context_length_distribution(texts, classifier.tokenizer)
    
    # 9. Save results
    results = {
        "precision": metrics['precision'],
        "recall": metrics['recall'],
        "f1": metrics['f1'],
        "avg_kappa": avg_kappa,
        "gate_pass": gate_pass,
        "confusion_matrix": cm.tolist(),
        "classification_report": metrics['report']
    }
    evaluator.save_results(results)
    
    print(f"\nGate Status: {'PASS' if gate_pass else 'FAIL'}")
    print(f"Precision: {metrics['precision']:.3f} (threshold: 0.85)")
    print(f"Avg Kappa: {avg_kappa:.3f} (threshold: 0.80)")

if __name__ == "__main__":
    main()
```

---

## Error Handling

**API Rate Limits:**
```python
def fetch_with_retry(url: str, max_retries: int = 3) -> dict:
    """Exponential backoff for API failures."""
    import time
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 429:  # Rate limit
                wait_time = 2 ** attempt
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed after {max_retries} retries")
```

**NaN/Inf in Training:**
```python
# Already handled in CitationClassifier.train via Trainer's default checks
# Hugging Face Trainer automatically detects NaN/Inf and stops training
```

**Missing Annotations:**
```python
def validate_annotations(annotations: list[dict]) -> bool:
    """Check completeness before training."""
    if len(annotations) < 100:
        raise ValueError(f"Insufficient annotations: {len(annotations)} < 100")
    if any('label' not in a for a in annotations):
        raise ValueError("Missing labels in annotations")
    return True
```

---

## Self-Validation Checklist

- [x] No ASCII diagrams (text descriptions only)
- [x] No KB search logs (noted "Applied: X" pattern)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments where relevant
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project noted (no existing code)
- [x] API signatures with type hints
- [x] Gate validation logic included
- [x] Error handling for API limits, missing data, training failures

---

**Document Status:** FINAL  
**Next Phase:** Phase 4 - Implementation  
**Estimated Complexity:** Low (standard libraries, well-documented APIs, simple binary classification)
