# Logic Design: h-m-integrated

**Document Type**: Logic Design
**Hypothesis ID**: h-m-integrated
**Hypothesis Type**: MECHANISM
**Created Date**: 2026-07-13
**Infrastructure Tier**: STANDARD

---

## Applied Patterns

Applied: PyTorch-style calibration API (fit/predict separation pattern)
Applied: Ensemble uncertainty quantification (from HuggingFace diffusers)
Applied: Weighted nonconformity scoring for conformal prediction

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code
**Analyzed Path**: docs/youra_research/h-e1/code/src/
**Relevant Symbols**: ConsistencyScorer, ConformalPredictor, LlamaGenerator, MultiDatasetLoader

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from base hypothesis. Signatures verified from actual implementation:

```python
# From: h-e1/code/src/consistency_scorer.py (ACTUAL CODE)
class ConsistencyScorer:
    def __init__(
        self,
        nli_model: str = "roberta-large-mnli",
        bertscore_model: str = "microsoft/deberta-xlarge-mnli",
        device: str = "cuda"
    ): ...
    
    def compute_consistency(
        self,
        reference: str,
        samples: list[str]
    ) -> float:
        """Compute ensemble consistency score C ∈ [0, 1]."""
        ...

# From: h-e1/code/src/conformal_predictor.py (ACTUAL CODE)
class ConformalPredictor:
    def __init__(
        self,
        coverage_target: float = 0.9,
        alpha: float = 0.1
    ): ...
    
    def calibrate(
        self,
        calibration_data: list[tuple[float, bool]]
    ) -> None:
        """Calibrate on (conformity_score, is_correct) pairs."""
        ...
    
    def construct_interval(
        self,
        conformity_score: float
    ) -> int:
        """Returns 1 if in interval, 0 otherwise."""
        ...
    
    def compute_coverage(
        self,
        test_data: list[tuple[float, bool]]
    ) -> float:
        """Compute empirical coverage rate."""
        ...

# From: h-e1/code/src/baseline_model.py (ACTUAL CODE)
class LlamaGenerator:
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-hf",
        device: str = "cuda"
    ): ...
    
    def generate_single(
        self,
        input_text: str,
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> str:
        """Generate single completion."""
        ...
    
    def generate_multiple(
        self,
        input_text: str,
        num_samples: int = 5,
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> list[str]:
        """Generate multiple diverse completions."""
        ...

# From: h-e1/code/src/data_loader.py (ACTUAL CODE)
class MultiDatasetLoader:
    def __init__(
        self,
        datasets: list[str],
        tokenizer_name: str = "meta-llama/Llama-2-7b-hf",
        max_length: int = 512,
        calibration_size: int = 1000,
        test_size: int = 1000
    ): ...
    
    def load_dataset(self, name: str, split: str = "validation") -> Dataset: ...
    
    def get_dataloader(
        self,
        dataset: Dataset,
        batch_size: int = 8,
        shuffle: bool = False
    ) -> DataLoader: ...
```

**Verified from**: h-e1/code/src/ (actual implementation, NOT spec!)

---

## M-1: HBC Core Implementation [Complexity: 15, Budget: 4]

**Applied**: Hierarchical Bayesian updating with mutual calibration

### API Signatures

```python
class HierarchicalBayesianCalibrator:
    """Three-step HBC mechanism with mutual calibration."""
    
    def __init__(
        self,
        consistency_scorer: ConsistencyScorer,
        conformal_predictor: ConformalPredictor,
        generator: LlamaGenerator,
        alpha: float = 0.1,
        max_iterations: int = 3,
        initial_threshold: float = 0.5
    ):
        """Initialize HBC calibrator."""
        self.consistency_scorer = consistency_scorer
        self.conformal_predictor = conformal_predictor
        self.generator = generator
        self.alpha = alpha
        self.max_iterations = max_iterations
        self.consistency_threshold = initial_threshold
        self.weighted_scores: list[float] = []
    
    def calibrate(
        self,
        calibration_data: list[dict]  # [{"question": str, "answer": str}, ...]
    ) -> None:
        """
        Calibrate HBC with mutual updating (Step 3).
        
        calibration_data: List of question-answer pairs
        
        Algorithm:
            FOR iteration in range(max_iterations):
                # Step 1: Consistency priors
                C_scores = []
                FOR sample in calibration_data:
                    samples = generator.generate_multiple(sample["question"])
                    C = consistency_scorer.compute_consistency(samples[0], samples[1:])
                    C_scores.append(C)
                
                # Step 2: Weighted conformal calibration
                weighted_data = []
                FOR i, sample in enumerate(calibration_data):
                    pred = samples[i][0]
                    true_ans = sample["answer"]
                    is_correct = evaluate_correctness(pred, true_ans)
                    
                    # Weighted nonconformity
                    base_score = 1.0 - similarity(pred, true_ans)
                    weighted_score = base_score / (1.0 + C_scores[i])
                    weighted_data.append((weighted_score, is_correct))
                
                conformal_predictor.calibrate(weighted_data)
                
                # Step 3: Update consistency threshold
                coverage = conformal_predictor.compute_coverage(weighted_data)
                IF coverage < 0.90:
                    consistency_threshold *= 1.1  # Relax
                ELSE IF coverage > 0.95:
                    consistency_threshold *= 0.9  # Tighten
        """
        pass
    
    def predict_with_uncertainty(
        self,
        query: str
    ) -> dict:
        """
        Predict with HBC uncertainty estimates.
        
        query: Input question
        
        Returns:
            {
                "prediction": str,
                "consistency_score": float,  # C(x)
                "in_interval": int,  # I(x) binary
                "confidence": float  # Combined
            }
        
        Algorithm:
            samples = generator.generate_multiple(query, num_samples=5)
            C = consistency_scorer.compute_consistency(samples[0], samples[1:])
            
            # Weighted conformity
            base_score = compute_base_conformity(samples[0])
            weighted_score = base_score / (1.0 + C)
            I = conformal_predictor.construct_interval(weighted_score)
            
            confidence = (C + I) / 2  # Simple ensemble
            
            RETURN {
                "prediction": samples[0],
                "consistency_score": C,
                "in_interval": I,
                "confidence": confidence
            }
        """
        pass
    
    def _compute_weighted_nonconformity(
        self,
        y_pred: str,
        y_true: str,
        consistency_score: float
    ) -> float:
        """
        Compute weighted nonconformity score.
        
        Formula: score = base_score / (1 + C)
        Rationale: High C → low epistemic → tighter intervals
        """
        pass
    
    def _update_consistency_threshold(
        self,
        coverage_results: list[float]
    ) -> float:
        """
        Update threshold based on coverage feedback.
        
        Returns new threshold value.
        """
        pass
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Consistency Prior Module | Step 1 implementation with C(x) computation |
| L-1-2 | Weighted Conformal Module | Step 2 with epistemic-weighted nonconformity |
| L-1-3 | Mutual Calibration Loop | Step 3 bidirectional threshold updating |
| L-1-4 | Inference Pipeline | Co-calibrated prediction with uncertainty |

---

## M-2: Baseline Suite [Complexity: 14, Budget: 4]

**Applied**: Independent calibration protocols for each baseline

### API Signatures

```python
# Baseline 1: SelfCheckGPT-only
class SelfCheckGPTBaseline:
    """Consistency-only baseline with threshold optimization."""
    
    def __init__(
        self,
        consistency_scorer: ConsistencyScorer,
        generator: LlamaGenerator,
        threshold: float = 0.5
    ):
        """Initialize SelfCheckGPT baseline."""
        self.consistency_scorer = consistency_scorer
        self.generator = generator
        self.threshold = threshold
        self.optimal_threshold = threshold
    
    def calibrate(
        self,
        calibration_data: list[dict]
    ) -> None:
        """
        Optimize threshold on calibration set.
        
        Algorithm:
            thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
            best_f1 = 0
            FOR t in thresholds:
                f1 = evaluate_threshold(t, calibration_data)
                IF f1 > best_f1:
                    best_f1 = f1
                    optimal_threshold = t
        """
        pass
    
    def predict(
        self,
        query: str
    ) -> dict:
        """
        Predict with consistency-only.
        
        Returns: {"prediction": str, "consistency": float, "is_hallucination": bool}
        """
        pass

# Baseline 2: COIN-only
class COINBaseline:
    """Conformal-only baseline (no consistency priors)."""
    
    def __init__(
        self,
        conformal_predictor: ConformalPredictor,
        generator: LlamaGenerator,
        alpha: float = 0.1
    ):
        """Initialize COIN baseline."""
        self.conformal_predictor = conformal_predictor
        self.generator = generator
        self.alpha = alpha
    
    def calibrate(
        self,
        calibration_data: list[dict]
    ) -> None:
        """
        Standard conformal calibration (no weighting).
        
        Algorithm:
            conformity_data = []
            FOR sample in calibration_data:
                pred = generator.generate_single(sample["question"])
                score = base_conformity(pred, sample["answer"])
                is_correct = evaluate(pred, sample["answer"])
                conformity_data.append((score, is_correct))
            
            conformal_predictor.calibrate(conformity_data)
        """
        pass
    
    def predict(
        self,
        query: str
    ) -> dict:
        """Returns: {"prediction": str, "in_interval": int, "conformity": float}"""
        pass

# Baseline 3: Independent Cascade
class IndependentCascadeBaseline:
    """Sequential SelfCheckGPT → COIN without joint calibration."""
    
    def __init__(
        self,
        selfcheck: SelfCheckGPTBaseline,
        coin: COINBaseline
    ):
        """Initialize cascade baseline."""
        self.selfcheck = selfcheck
        self.coin = coin
    
    def calibrate(
        self,
        calibration_data: list[dict]
    ) -> None:
        """
        Calibrate independently.
        
        Algorithm:
            selfcheck.calibrate(calibration_data)
            coin.calibrate(calibration_data)
        """
        pass
    
    def predict(
        self,
        query: str
    ) -> dict:
        """
        Sequential filtering.
        
        Algorithm:
            selfcheck_result = selfcheck.predict(query)
            IF selfcheck_result["is_hallucination"]:
                RETURN {"prediction": "ABSTAIN", "reason": "low_consistency"}
            
            coin_result = coin.predict(query)
            RETURN {
                "prediction": coin_result["prediction"],
                "consistency": selfcheck_result["consistency"],
                "in_interval": coin_result["in_interval"]
            }
        """
        pass
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | SelfCheckGPT Module | Consistency-only with threshold grid search |
| L-2-2 | COIN Module | Standard conformal without epistemic weighting |
| L-2-3 | Cascade Module | Independent two-stage filtering |
| L-2-4 | Baseline Evaluation | Unified interface for all baselines |

---

## Shared Modules (No Budget - Utility)

### ECE Metric (`ece_metric.py`)

```python
class ECEMetric:
    """Expected Calibration Error computation."""
    
    def __init__(self, n_bins: int = 10):
        self.n_bins = n_bins
    
    def compute(
        self,
        predictions: np.ndarray,  # [N]
        ground_truth: np.ndarray,  # [N]
        confidences: np.ndarray  # [N]
    ) -> float:
        """
        Compute ECE.
        
        Algorithm:
            bins = linspace(0, 1, n_bins + 1)
            ece = 0
            FOR i in range(n_bins):
                mask = (confidences >= bins[i]) & (confidences < bins[i+1])
                IF sum(mask) > 0:
                    bin_acc = mean(predictions[mask] == ground_truth[mask])
                    bin_conf = mean(confidences[mask])
                    bin_weight = sum(mask) / N
                    ece += bin_weight * abs(bin_acc - bin_conf)
            RETURN ece
        """
        pass
    
    def compute_per_bin_stats(
        self,
        predictions: np.ndarray,
        ground_truth: np.ndarray,
        confidences: np.ndarray
    ) -> dict:
        """Returns: {bin_i: {"accuracy": float, "confidence": float, "count": int}}"""
        pass
```

### Computational Cost Tracker (`cost_tracker.py`)

```python
class ComputationalCostTracker:
    """Track forward passes for all methods."""
    
    def __init__(self):
        self.forward_counts: dict[str, int] = {}
    
    def reset(self) -> None:
        """Reset all counters."""
        self.forward_counts = {}
    
    def log_forward_pass(self, model_name: str, batch_size: int = 1) -> None:
        """Increment counter. model_name: "llama", "nli", "bertscore", etc."""
        pass
    
    def get_total_cost(self) -> int:
        """Returns total forward passes across all models."""
        pass
    
    def get_cost_breakdown(self) -> dict:
        """Returns: {"llama": int, "nli": int, ...}"""
        pass
    
    def compute_reduction(self, baseline_cost: int) -> float:
        """Returns: (baseline_cost - total_cost) / baseline_cost"""
        pass
```

### Ablation Study (`ablation_study.py`)

```python
class AblationStudy:
    """Sweet spot validation (ρ ~ 0.5 dependency)."""
    
    def __init__(
        self,
        hbc: HierarchicalBayesianCalibrator,
        ece_metric: ECEMetric
    ):
        self.hbc = hbc
        self.ece_metric = ece_metric
    
    def simulate_correlation_levels(
        self,
        rho_values: list[float],  # [0.2, 0.35, 0.5, 0.65, 0.8]
        test_data: list[dict]
    ) -> dict:
        """
        Perturb correlations and measure ECE.
        
        Returns: {rho: ece_value}
        
        Algorithm:
            results = {}
            FOR rho in rho_values:
                # Perturb consistency scores to achieve target rho
                perturbed_C = perturb_consistency_scores(original_C, target_rho=rho)
                
                # Re-run HBC with perturbed C
                ece = run_hbc_with_fixed_C(perturbed_C, test_data)
                results[rho] = ece
            
            RETURN results
        """
        pass
    
    def perturb_consistency_scores(
        self,
        original_scores: np.ndarray,
        target_rho: float
    ) -> np.ndarray:
        """
        Add controlled noise to achieve target ρ(C, I).
        
        Algorithm:
            noise = randn(len(original_scores))
            noise = noise * (1 - target_rho**2)**0.5
            perturbed = original_scores * target_rho + noise
            RETURN clip(perturbed, 0, 1)
        """
        pass
    
    def validate_sweet_spot(self, results: dict) -> bool:
        """
        Check if minimum ECE is at ρ ~ 0.5.
        
        Returns: True if argmin(ECE) ∈ [0.4, 0.6]
        """
        pass
```

### Multi-Method Evaluator (`multi_method_evaluator.py`)

```python
class MultiMethodEvaluator:
    """Unified evaluation framework for all methods."""
    
    def __init__(
        self,
        methods: dict,  # {"HBC": hbc, "SelfCheck": selfcheck, ...}
        datasets: list[str],
        ece_metric: ECEMetric,
        cost_tracker: ComputationalCostTracker
    ):
        self.methods = methods
        self.datasets = datasets
        self.ece_metric = ece_metric
        self.cost_tracker = cost_tracker
    
    def run_all_experiments(self) -> dict:
        """
        Run all methods on all datasets.
        
        Returns: {
            dataset: {
                method: {
                    "ece": float,
                    "coverage": float,
                    "cost": int,
                    "predictions": list
                }
            }
        }
        """
        pass
    
    def evaluate_single_method(
        self,
        method_name: str,
        method: object,
        dataset_name: str
    ) -> dict:
        """Evaluate one method on one dataset."""
        pass
    
    def compute_statistical_significance(
        self,
        hbc_ece: np.ndarray,  # [n_runs]
        baseline_ece: np.ndarray  # [n_runs]
    ) -> tuple[float, float]:
        """
        Two-tailed t-test.
        
        Returns: (t_statistic, p_value)
        """
        pass
    
    def check_gate_criteria(self, results: dict) -> bool:
        """
        Validate all gate conditions.
        
        Checks:
            1. ECE_HBC < 0.05
            2. p < 0.05 vs all baselines
            3. Cost reduction 30-50%
            4. Coverage >= 0.90
        
        Returns: True if all pass
        """
        pass
```

### Visualization Generator (`visualization_generator.py`)

```python
class VisualizationGenerator:
    """Generate 5 required figures."""
    
    def __init__(self, output_dir: str = "figures/"):
        self.output_dir = output_dir
    
    def plot_ece_comparison(self, results: dict) -> None:
        """Bar chart: ECE for all 4 methods × 3 datasets."""
        pass
    
    def plot_reliability_diagrams(self, results: dict) -> None:
        """4 subplots: reliability curves for each method."""
        pass
    
    def plot_cost_quality_tradeoff(self, results: dict) -> None:
        """Scatter: cost (x) vs ECE (y) for all methods."""
        pass
    
    def plot_coverage_comparison(self, results: dict) -> None:
        """Bar chart: coverage for HBC, COIN, Cascade."""
        pass
    
    def plot_ablation_sweet_spot(self, ablation_results: dict) -> None:
        """Line plot: ρ (x) vs ECE (y), highlight minimum."""
        pass
    
    def generate_all_figures(self, results: dict, ablation_results: dict) -> None:
        """Generate all 5 figures in one call."""
        pass
```

---

## Main Execution Flow (`train.py`)

```python
def main():
    # 1. Load config
    config = load_config("config.py")
    
    # 2. Initialize base components
    loader = MultiDatasetLoader(
        datasets=config["datasets"]["names"],
        tokenizer_name=config["model"]["name"],
        max_length=config["datasets"]["max_length"],
        calibration_size=config["datasets"]["calibration_size"],
        test_size=config["datasets"]["test_size"]
    )
    generator = LlamaGenerator(model_name=config["model"]["name"])
    consistency_scorer = ConsistencyScorer(
        nli_model=config["consistency"]["nli_model"],
        bertscore_model=config["consistency"]["bertscore_model"]
    )
    conformal_predictor = ConformalPredictor(
        coverage_target=config["conformal"]["coverage_target"],
        alpha=config["hbc"]["alpha"]
    )
    
    # 3. Initialize methods
    hbc = HierarchicalBayesianCalibrator(
        consistency_scorer=consistency_scorer,
        conformal_predictor=conformal_predictor,
        generator=generator,
        alpha=config["hbc"]["alpha"],
        max_iterations=config["hbc"]["max_iterations"]
    )
    selfcheck = SelfCheckGPTBaseline(
        consistency_scorer=consistency_scorer,
        generator=generator
    )
    coin = COINBaseline(
        conformal_predictor=conformal_predictor,
        generator=generator,
        alpha=config["baselines"]["coin_alpha"]
    )
    cascade = IndependentCascadeBaseline(
        selfcheck=selfcheck,
        coin=coin
    )
    
    methods = {
        "HBC": hbc,
        "SelfCheck": selfcheck,
        "COIN": coin,
        "Cascade": cascade
    }
    
    # 4. Initialize evaluation infrastructure
    ece_metric = ECEMetric(n_bins=config["evaluation"]["ece_bins"])
    cost_tracker = ComputationalCostTracker()
    evaluator = MultiMethodEvaluator(
        methods=methods,
        datasets=config["datasets"]["names"],
        ece_metric=ece_metric,
        cost_tracker=cost_tracker
    )
    
    # 5. Run experiments
    results = evaluator.run_all_experiments()
    
    # 6. Ablation study
    ablation = AblationStudy(hbc=hbc, ece_metric=ece_metric)
    test_data = loader.load_dataset("truthful_qa", split="test")
    ablation_results = ablation.simulate_correlation_levels(
        rho_values=config["ablation"]["rho_values"],
        test_data=test_data
    )
    
    # 7. Gate validation
    gate_pass = evaluator.check_gate_criteria(results)
    sweet_spot_pass = ablation.validate_sweet_spot(ablation_results)
    
    # 8. Generate visualizations
    viz = VisualizationGenerator(output_dir=config["output"]["figures_dir"])
    viz.generate_all_figures(results, ablation_results)
    
    # 9. Generate report
    generate_validation_report(
        results=results,
        ablation_results=ablation_results,
        gate_pass=gate_pass and sweet_spot_pass,
        output_path=config["output"]["report_path"]
    )
    
    RETURN gate_pass and sweet_spot_pass
```

---

## Tensor Shape Reference

| Component | Input Shape | Output Shape |
|-----------|-------------|--------------|
| LlamaGenerator.generate_multiple | text (str) | list[str] (5 samples) |
| ConsistencyScorer.compute_consistency | reference + list[str] | scalar C ∈ [0,1] |
| ConformalPredictor.construct_interval | scalar conformity | scalar I ∈ {0,1} |
| ECEMetric.compute | [N], [N], [N] | scalar ECE |
| CostTracker.get_total_cost | - | scalar (int) |

---

**Logic Design Status**: COMPLETE
**Ready for Phase 4 Implementation**: YES
**Total Subtasks Used**: 8/8 (4 for M-1 HBC Core + 4 for M-2 Baseline Suite)
