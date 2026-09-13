# Logic Design: h-e1

**Document Type**: Logic Design
**Hypothesis ID**: h-e1
**Hypothesis Type**: EXISTENCE
**Created Date**: 2026-07-13
**Infrastructure Tier**: LIGHT (minimal)

---

## Applied Patterns

Applied: PyTorch module API design patterns (forward methods with type hints)
Applied: Tensor shape documentation conventions (batch-first notation)
Applied: Statistical API patterns (separation of fit/predict)

---

## Codebase Analysis (Serena)

**Project Type**: Green-field
**Status**: No existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch - no prior code in hypothesis folder

---

## Module APIs

### 1. DataLoader Module (`data_loader.py`)

#### MultiDatasetLoader Class

```python
class MultiDatasetLoader:
    """Load and preprocess multiple datasets for UQ experiment."""
    
    def __init__(
        self,
        datasets: list[str],  # ["truthful_qa", "Anthropic/hh-rlhf", "squad"]
        tokenizer_name: str = "meta-llama/Llama-2-7b-hf",
        max_length: int = 512,
        calibration_size: int = 1000,
        test_size: int = 1000
    ):
        """Initialize multi-dataset loader."""
        pass
    
    def load_dataset(self, name: str, split: str = "validation") -> Dataset:
        """
        Load single dataset from HuggingFace.
        
        Args:
            name: Dataset identifier
            split: Data split to load
            
        Returns:
            Dataset: HuggingFace Dataset object
            
        Tensor Shapes:
            N/A - returns Dataset object
        """
        pass
    
    def preprocess(self, dataset: Dataset) -> Dataset:
        """
        Tokenize and preprocess dataset.
        
        Args:
            dataset: Raw dataset
            
        Returns:
            Dataset: Tokenized dataset
            
        Tensor Shapes:
            input_ids: [batch_size, max_length]
            attention_mask: [batch_size, max_length]
        """
        pass
    
    def get_dataloader(
        self,
        dataset: Dataset,
        batch_size: int = 8,
        shuffle: bool = False
    ) -> DataLoader:
        """
        Create PyTorch DataLoader.
        
        Returns:
            DataLoader yielding batches
        """
        pass
```

---

### 2. BaselineModel Module (`baseline_model.py`)

#### LlamaGenerator Class

```python
class LlamaGenerator:
    """Llama-2-7B generation with multi-sampling capability."""
    
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-hf",
        device: str = "cuda"
    ):
        """Load Llama-2-7B model."""
        pass
    
    def generate_single(
        self,
        input_text: str,
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> str:
        """
        Generate single completion.
        
        Args:
            input_text: Prompt text
            max_tokens: Maximum generation length
            temperature: Sampling temperature
            
        Returns:
            str: Generated text
            
        Tensor Shapes:
            input_ids: [1, seq_len]
            output_ids: [1, seq_len + max_tokens]
        """
        pass
    
    def generate_multiple(
        self,
        input_text: str,
        num_samples: int = 5,
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> list[str]:
        """
        Generate multiple diverse completions (for consistency scoring).
        
        Args:
            input_text: Prompt text
            num_samples: Number of samples to generate
            max_tokens: Maximum generation length
            temperature: Sampling temperature
            
        Returns:
            list[str]: List of generated texts
            
        Tensor Shapes:
            input_ids: [1, seq_len]
            output_ids: [num_samples, seq_len + max_tokens]
            
        Algorithm:
            FOR i in range(num_samples):
                sample_i = model.generate(input_ids, temperature=temperature)
                samples.append(sample_i)
            RETURN samples
        """
        pass
```

---

### 3. ConsistencyScorer Module (`consistency_scorer.py`)

#### ConsistencyScorer Class

```python
class ConsistencyScorer:
    """Compute epistemic uncertainty via NLI + BERTScore ensemble."""
    
    def __init__(
        self,
        nli_model: str = "roberta-large-mnli",
        bertscore_model: str = "deberta-xlarge-mnli"
    ):
        """Initialize NLI and BERTScore models."""
        pass
    
    def compute_nli_scores(
        self,
        reference: str,
        samples: list[str]
    ) -> list[float]:
        """
        Compute NLI entailment scores.
        
        Args:
            reference: Main generated answer
            samples: Alternative generated samples
            
        Returns:
            list[float]: Entailment probabilities [0, 1]
            
        Tensor Shapes:
            nli_input: [num_samples, 2, max_len]  # (premise, hypothesis) pairs
            nli_logits: [num_samples, 3]  # (contradiction, neutral, entailment)
            entailment_probs: [num_samples]
            
        Algorithm:
            FOR sample in samples:
                logits = nli_model(reference, sample)
                entailment_prob = softmax(logits)[2]  # Index 2 = entailment
                scores.append(entailment_prob)
            RETURN scores
        """
        pass
    
    def compute_bertscore(
        self,
        reference: str,
        samples: list[str]
    ) -> list[float]:
        """
        Compute BERTScore F1 similarities.
        
        Args:
            reference: Main generated answer
            samples: Alternative generated samples
            
        Returns:
            list[float]: F1 scores [0, 1]
            
        Tensor Shapes:
            embeddings_ref: [seq_len_ref, hidden_dim]
            embeddings_sample: [seq_len_sample, hidden_dim]
            similarity_matrix: [seq_len_ref, seq_len_sample]
            f1_score: scalar
        """
        pass
    
    def compute_consistency(
        self,
        reference: str,
        samples: list[str]
    ) -> float:
        """
        Compute ensemble consistency score C.
        
        Args:
            reference: Main generated answer
            samples: Alternative generated samples (typically 5)
            
        Returns:
            float: Consistency score C ∈ [0, 1]
                   High C = low epistemic uncertainty
            
        Algorithm:
            nli_scores = compute_nli_scores(reference, samples)
            bert_scores = compute_bertscore(reference, samples)
            
            # Ensemble average
            C = (mean(nli_scores) + mean(bert_scores)) / 2
            
            RETURN C
        """
        pass
```

---

### 4. ConformalPredictor Module (`conformal_predictor.py`)

#### ConformalPredictor Class

```python
class ConformalPredictor:
    """Conformal prediction with coverage guarantees (aleatoric uncertainty)."""
    
    def __init__(
        self,
        coverage_target: float = 0.9,  # 90% coverage
        alpha: float = 0.1
    ):
        """Initialize conformal predictor."""
        self.coverage_target = coverage_target
        self.alpha = alpha
        self.calibration_scores: list[float] = []
        self.quantile_threshold: float = 0.0
    
    def calibrate(
        self,
        calibration_samples: list[tuple[str, str]]  # [(question, answer), ...]
    ) -> None:
        """
        Calibrate conformal predictor on calibration set.
        
        Args:
            calibration_samples: List of (input, true_output) pairs
            
        Side Effects:
            Sets self.quantile_threshold based on calibration scores
            
        Tensor Shapes:
            conformity_scores: [calibration_size]
            quantile_threshold: scalar
            
        Algorithm:
            conformity_scores = []
            FOR (question, true_answer) in calibration_samples:
                predicted = model.generate(question)
                score = conformity_function(predicted, true_answer)
                conformity_scores.append(score)
            
            # Compute quantile for desired coverage
            n = len(conformity_scores)
            q = ceil((n + 1) * (1 - alpha)) / n
            quantile_threshold = quantile(conformity_scores, q)
            
            self.quantile_threshold = quantile_threshold
        """
        pass
    
    def predict_interval(
        self,
        input_text: str,
        predicted_output: str
    ) -> tuple[bool, float]:
        """
        Construct conformal prediction interval and check membership.
        
        Args:
            input_text: Input question
            predicted_output: Model's predicted answer
            
        Returns:
            tuple[bool, float]:
                - I_binary: 1 if in interval, 0 otherwise
                - conformity_score: Raw conformity score
            
        Tensor Shapes:
            conformity_score: scalar
            I_binary: scalar (0 or 1)
            
        Algorithm:
            conformity_score = conformity_function(predicted_output, input_text)
            
            # Check if within calibrated threshold
            I_binary = 1 if conformity_score <= quantile_threshold else 0
            
            RETURN (I_binary, conformity_score)
        """
        pass
    
    def conformity_function(
        self,
        predicted: str,
        true_answer: str
    ) -> float:
        """
        Compute conformity score (lower = more conforming).
        
        Args:
            predicted: Model prediction
            true_answer: Ground truth
            
        Returns:
            float: Conformity score (e.g., negative log-likelihood or error metric)
            
        Algorithm:
            # Simple implementation: character-level edit distance
            score = edit_distance(predicted, true_answer) / max(len(predicted), len(true_answer))
            RETURN score
        """
        pass
```

---

### 5. CorrelationAnalyzer Module (`correlation_analyzer.py`)

#### CorrelationAnalyzer Class

```python
class CorrelationAnalyzer:
    """Compute Pearson correlation ρ(C, I) and statistical tests."""
    
    def __init__(self):
        """Initialize analyzer."""
        pass
    
    def compute_pearson_correlation(
        self,
        consistency_scores: list[float],  # C values
        interval_membership: list[int]    # I_binary values (0 or 1)
    ) -> tuple[float, float]:
        """
        Compute Pearson correlation coefficient.
        
        Args:
            consistency_scores: List of C scores
            interval_membership: List of I_binary indicators
            
        Returns:
            tuple[float, float]: (rho, p_value)
            
        Tensor Shapes:
            consistency_scores: [n_samples]
            interval_membership: [n_samples]
            rho: scalar
            p_value: scalar
            
        Algorithm:
            from scipy.stats import pearsonr
            
            rho, p_value = pearsonr(consistency_scores, interval_membership)
            
            RETURN (rho, p_value)
        """
        pass
    
    def validate_gate_condition(
        self,
        rho: float,
        p_value: float,
        rho_min: float = 0.3,
        rho_max: float = 0.7,
        p_threshold: float = 0.05
    ) -> bool:
        """
        Check if correlation meets gate criteria.
        
        Args:
            rho: Pearson correlation coefficient
            p_value: Statistical significance p-value
            rho_min: Lower bound for gate
            rho_max: Upper bound for gate
            p_threshold: Significance threshold
            
        Returns:
            bool: True if gate passes
            
        Algorithm:
            gate_pass = (rho_min <= rho <= rho_max) AND (p_value < p_threshold)
            RETURN gate_pass
        """
        pass
    
    def compute_per_dataset_correlation(
        self,
        results: dict[str, tuple[list[float], list[int]]]
    ) -> dict[str, tuple[float, float]]:
        """
        Compute correlation for each dataset separately.
        
        Args:
            results: Dict mapping dataset_name -> (C_scores, I_binary)
            
        Returns:
            dict: Dataset name -> (rho, p_value)
            
        Algorithm:
            correlations = {}
            FOR dataset_name, (C_scores, I_binary) in results.items():
                rho, p_value = compute_pearson_correlation(C_scores, I_binary)
                correlations[dataset_name] = (rho, p_value)
            RETURN correlations
        """
        pass
```

---

### 6. Evaluator Module (`evaluator.py`)

#### ExperimentEvaluator Class

```python
class ExperimentEvaluator:
    """Run full experiment and generate validation report."""
    
    def __init__(
        self,
        datasets: list[str],
        num_samples: int = 5,
        output_dir: str = "."
    ):
        """Initialize evaluator with dataset list."""
        pass
    
    def run_experiment(
        self,
        dataset_name: str
    ) -> dict:
        """
        Execute full experiment pipeline on one dataset.
        
        Args:
            dataset_name: Dataset to evaluate
            
        Returns:
            dict: Results containing C_scores, I_binary, rho, p_value, coverage
            
        Algorithm:
            # 1. Load data
            loader = MultiDatasetLoader([dataset_name])
            test_data = loader.load_dataset(dataset_name, "test")
            
            # 2. Generate and score
            C_scores = []
            I_binary = []
            FOR sample in test_data:
                # Generate multiple samples
                samples = generator.generate_multiple(sample.question, num_samples=5)
                
                # Consistency score (epistemic)
                C = consistency_scorer.compute_consistency(samples[0], samples[1:])
                C_scores.append(C)
                
                # Conformal interval (aleatoric)
                I, _ = conformal_predictor.predict_interval(sample.question, samples[0])
                I_binary.append(I)
            
            # 3. Correlation analysis
            rho, p_value = correlation_analyzer.compute_pearson_correlation(C_scores, I_binary)
            
            # 4. Coverage
            coverage = mean(I_binary)
            
            RETURN {
                "C_scores": C_scores,
                "I_binary": I_binary,
                "rho": rho,
                "p_value": p_value,
                "coverage": coverage
            }
        """
        pass
    
    def compute_ece(
        self,
        predictions: list[float],
        labels: list[int],
        n_bins: int = 10
    ) -> float:
        """
        Compute Expected Calibration Error.
        
        Args:
            predictions: Predicted confidence scores
            labels: True binary labels
            n_bins: Number of calibration bins
            
        Returns:
            float: ECE score
            
        Tensor Shapes:
            predictions: [n_samples]
            labels: [n_samples]
            ece: scalar
            
        Algorithm:
            bins = linspace(0, 1, n_bins + 1)
            ece = 0
            
            FOR i in range(n_bins):
                bin_mask = (predictions >= bins[i]) & (predictions < bins[i+1])
                if sum(bin_mask) > 0:
                    bin_conf = mean(predictions[bin_mask])
                    bin_acc = mean(labels[bin_mask])
                    bin_weight = sum(bin_mask) / len(predictions)
                    ece += bin_weight * abs(bin_conf - bin_acc)
            
            RETURN ece
        """
        pass
    
    def generate_visualizations(
        self,
        results: dict,
        output_dir: str
    ) -> None:
        """
        Generate 5 required figures.
        
        Args:
            results: Experiment results dict
            output_dir: Directory to save figures
            
        Figures:
            1. gate_metrics.png - Bar chart: target vs actual ρ
            2. scatter_C_vs_I.png - Scatter: C vs I_binary
            3. distribution_comparison.png - Histograms: C for I=1 vs I=0
            4. per_dataset_correlation.png - Bar chart: ρ for each dataset
            5. calibration_curve.png - ECE visualization
        """
        pass
    
    def generate_report(
        self,
        results: dict,
        output_path: str
    ) -> None:
        """
        Generate 04_validation.md report.
        
        Args:
            results: Experiment results dict
            output_path: Path to save markdown report
            
        Report Sections:
            - Gate Metrics (ρ, p-value, coverage)
            - Per-Dataset Results
            - Pass/Fail Determination
            - Visualizations (embedded figure paths)
        """
        pass
```

---

## Pseudo-Code: Main Experiment Flow

```python
# train.py - Main execution script

def main():
    # 1. Initialize components
    config = load_config()
    loader = MultiDatasetLoader(
        datasets=config["datasets"]["names"],
        tokenizer_name=config["model"]["name"],
        max_length=config["datasets"]["max_length"]
    )
    generator = LlamaGenerator(model_name=config["model"]["name"])
    consistency_scorer = ConsistencyScorer(
        nli_model=config["consistency"]["nli_model"]
    )
    conformal_predictor = ConformalPredictor(
        coverage_target=config["conformal"]["coverage_target"]
    )
    correlation_analyzer = CorrelationAnalyzer()
    evaluator = ExperimentEvaluator(
        datasets=config["datasets"]["names"],
        num_samples=config["model"]["num_samples"]
    )
    
    # 2. Calibrate conformal predictor
    FOR dataset_name IN config["datasets"]["names"]:
        calibration_data = loader.load_dataset(dataset_name, split="calibration")
        conformal_predictor.calibrate(calibration_data)
    
    # 3. Run experiment on all datasets
    all_results = {}
    FOR dataset_name IN config["datasets"]["names"]:
        results = evaluator.run_experiment(dataset_name)
        all_results[dataset_name] = results
        
        print(f"{dataset_name}: ρ = {results['rho']:.3f}, p = {results['p_value']:.4f}")
    
    # 4. Validate gate condition
    gate_pass = True
    FOR dataset_name, results IN all_results.items():
        dataset_pass = correlation_analyzer.validate_gate_condition(
            rho=results["rho"],
            p_value=results["p_value"]
        )
        gate_pass = gate_pass AND dataset_pass
    
    # 5. Generate visualizations and report
    evaluator.generate_visualizations(all_results, output_dir="figures/")
    evaluator.generate_report(all_results, output_path="04_validation.md")
    
    # 6. Print final verdict
    IF gate_pass:
        print("✓ GATE PASSED: 0.3 ≤ ρ ≤ 0.7 on all datasets with p < 0.05")
    ELSE:
        print("✗ GATE FAILED: Hypothesis falsified")
    
    RETURN gate_pass

if __name__ == "__main__":
    main()
```

---

## Data Flow Summary

```
Input Question
    ↓
[LlamaGenerator] → 5 samples
    ↓
[ConsistencyScorer] → C score (epistemic)
    ↓
[ConformalPredictor] → I_binary (aleatoric)
    ↓
[CorrelationAnalyzer] → ρ(C, I), p-value
    ↓
[ExperimentEvaluator] → Gate validation, figures, report
```

---

## Tensor Shape Reference

| Component | Input Shape | Output Shape |
|-----------|-------------|--------------|
| DataLoader | text (string) | [batch, seq_len] |
| LlamaGenerator | [1, seq_len] | [num_samples, seq_len + max_tokens] |
| ConsistencyScorer (NLI) | [num_samples, 2, max_len] | [num_samples] → scalar |
| ConsistencyScorer (BERT) | [seq_len, hidden_dim] | scalar |
| ConformalPredictor | scalar conformity | scalar I_binary |
| CorrelationAnalyzer | [n_samples], [n_samples] | scalar ρ, scalar p |

---

**Logic Design Status**: COMPLETE
**Ready for Phase 4 Implementation**: YES
