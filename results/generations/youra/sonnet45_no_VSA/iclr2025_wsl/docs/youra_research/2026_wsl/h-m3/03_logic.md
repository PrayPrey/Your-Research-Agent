# Logic Specification: H-M3 Checkpoint Extraction Feasibility

**Hypothesis ID:** h-m3  
**Type:** MECHANISM (MUST_WORK gate)  
**Date:** 2026-07-11  
**Status:** Ready for Phase 4 Implementation  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extending h-m2 validated codebase (feature extraction proven, StatisticalFeatureExtractor available)  
**Analyzed Path:** `docs/youra_research/h-m2/code/`  
**Relevant Symbols:** StatisticalFeatureExtractor, NORM_PATTERNS, HEAD_KEYWORDS, MODEL_FAMILIES  
**Code Reuse:** 100% feature extraction logic reused from h-m2, new timing/monitoring modules

---

## Knowledge Base Patterns Applied

**Applied:** Python time.perf_counter() for high-precision timing, torch.cuda.memory_allocated() for GPU monitoring, matplotlib subplots for timing visualization

---

## A-1: CheckpointOnlyExtractor [Complexity: 14, Budget: 14/14]

**Applied:** PyTorch weights_only=True checkpoint loading with StatisticalFeatureExtractor

### API Signatures

```python
class CheckpointOnlyExtractor:
    def __init__(self, cache_dir: str = ".cache/checkpoints"):
        """Initialize extractor with checkpoint cache directory."""
        self.cache_dir = cache_dir
        self.feature_extractor = StatisticalFeatureExtractor()
    
    def extract_batch(self, model_names: list[str]) -> dict:
        """
        Extract features from checkpoints using weights_only=True.
        
        Args:
            model_names: List of TIMM model names
        
        Returns:
            {
                'total_time': float,
                'per_model_times': dict[str, float],
                'features': pd.DataFrame,  # [model_name, family, 5 features]
                'failed_models': list[str]
            }
        """
        ...
    
    def _load_checkpoint_weights_only(self, model_name: str) -> dict:
        """Load checkpoint with weights_only=True security flag. Returns state_dict."""
        ...
    
    def _download_checkpoint(self, model_name: str) -> str:
        """Download TIMM checkpoint if not cached. Returns checkpoint path."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| state_dict | dict | Keys: str, Values: tensors |
| features | (N, 5) | DataFrame: [bn, ln, gn, no_norm, R] |

### Pseudo-code

```
1. Initialize timer and results storage
2. For each model_name in model_names:
   start_time = perf_counter()
   
   # Download checkpoint if not cached
   checkpoint_path = self._download_checkpoint(model_name)
   
   # Load with security flag
   state_dict = torch.load(checkpoint_path, weights_only=True, map_location='cpu')
   
   # Extract features using h-m2 logic
   features = self.feature_extractor.extract_features(state_dict)
   
   end_time = perf_counter()
   per_model_times[model_name] = end_time - start_time
   
3. Compute total_time = sum(per_model_times.values())
4. Convert features to DataFrame
5. Return results dict
```

### Subtasks [14/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Checkpoint cache | Implement cache directory management |
| L-1-2 | TIMM download | Use timm.models.hub to download checkpoints |
| L-1-3 | Security loading | torch.load with weights_only=True, map_location='cpu' |
| L-1-4 | Feature extraction | Call StatisticalFeatureExtractor |
| L-1-5 | Timing per-model | perf_counter() for each model |
| L-1-6 | Error handling | Catch download/loading failures |
| L-1-7 | DataFrame export | Convert features to pandas DataFrame |

---

## A-2: ForwardPassExtractor [Complexity: 12, Budget: 12/12]

**Applied:** TIMM model instantiation with forward pass baseline

### API Signatures

```python
class ForwardPassExtractor:
    def __init__(self, device: str = "cpu"):
        """Initialize extractor with device."""
        self.device = device
        self.feature_extractor = StatisticalFeatureExtractor()
    
    def extract_batch(self, model_names: list[str]) -> dict:
        """
        Extract features WITH full model instantiation and forward pass.
        
        Args:
            model_names: List of TIMM model names (5-model subset)
        
        Returns:
            {
                'total_time': float,
                'per_model_times': dict[str, float],
                'features': pd.DataFrame
            }
        """
        ...
    
    def _instantiate_model(self, model_name: str):
        """Load model via timm.create_model(pretrained=True). Returns model."""
        ...
    
    def _run_forward_pass(self, model, input_shape: tuple = (1, 3, 224, 224)):
        """Run dummy forward pass. x: [1, 3, 224, 224] -> out: [1, num_classes]"""
        ...
```

### Pseudo-code

```
1. For each model_name in model_names:
   start_time = perf_counter()
   
   # Full model instantiation
   model = timm.create_model(model_name, pretrained=True)
   model.to(self.device)
   model.eval()
   
   # Dummy forward pass
   x = torch.randn(1, 3, 224, 224, device=self.device)
   with torch.no_grad():
       out = model(x)
   
   # Extract features from state_dict
   features = self.feature_extractor.extract_features(model.state_dict())
   
   end_time = perf_counter()
   per_model_times[model_name] = end_time - start_time
   
   # Free GPU memory
   del model, x, out
   torch.cuda.empty_cache()

2. Return results dict
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Model instantiation | timm.create_model(pretrained=True) |
| L-2-2 | Forward pass | Dummy inference with torch.no_grad() |
| L-2-3 | Feature extraction | Call StatisticalFeatureExtractor |
| L-2-4 | Timing measurement | perf_counter() per model |
| L-2-5 | Memory cleanup | Delete model, clear GPU cache |
| L-2-6 | DataFrame export | Convert features to DataFrame |

---

## A-3: TimingBenchmark [Complexity: 15, Budget: 15/15]

**Applied:** Python time.perf_counter() with warmup logic and matplotlib visualization

### API Signatures

```python
class TimingBenchmark:
    def __init__(self, warmup_runs: int = 1):
        """Initialize benchmark with warmup runs."""
        self.warmup_runs = warmup_runs
    
    def measure_extraction_time(self, extractor_fn, model_names: list[str]) -> dict:
        """
        Measure extraction time with warmup.
        
        Args:
            extractor_fn: Callable extraction function (extract_batch)
            model_names: Model list
        
        Returns:
            {
                'total_time': float,
                'avg_time': float,
                'median_time': float,
                'p90_time': float,
                'per_model': dict[str, float]
            }
        """
        ...
    
    def compare_methods(self, checkpoint_results: dict, forward_results: dict) -> dict:
        """
        Compute speedup between checkpoint-only and forward-pass.
        
        Returns:
            {
                'speedup_factor': float,
                'checkpoint_time': float,
                'forward_time': float,
                'per_model_speedup': dict[str, float]
            }
        """
        ...
    
    def plot_timing_comparison(self, results: dict, output_path: str):
        """Generate bar chart: checkpoint vs forward-pass timing."""
        ...
    
    def save_timing_report(self, results: dict, output_path: str):
        """Save timing metrics to JSON."""
        ...
```

### Pseudo-code

```
1. Warmup phase:
   for _ in range(self.warmup_runs):
       extractor_fn([model_names[0]])  # Exclude from timing

2. Measurement phase:
   start_time = perf_counter()
   results = extractor_fn(model_names)
   end_time = perf_counter()
   
3. Compute statistics:
   total_time = results['total_time']
   per_model_times = list(results['per_model_times'].values())
   avg_time = np.mean(per_model_times)
   median_time = np.median(per_model_times)
   p90_time = np.percentile(per_model_times, 90)

4. Speedup computation:
   speedup_factor = forward_total / checkpoint_total

5. Visualization:
   fig, ax = plt.subplots(1, 1, figsize=(10, 6))
   ax.bar(['Checkpoint-Only', 'Forward-Pass'], [checkpoint_time, forward_time])
   ax.set_ylabel('Time (seconds)')
   plt.savefig(output_path)
```

### Subtasks [15/15 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Warmup logic | Run 1 model extraction before timing |
| L-3-2 | perf_counter | High-precision timing wrapper |
| L-3-3 | Statistics | Compute avg, median, p90 |
| L-3-4 | Speedup | Ratio computation |
| L-3-5 | Bar chart | matplotlib visualization |
| L-3-6 | JSON export | Save timing results |

---

## A-4: GPUMonitor [Complexity: 11, Budget: 11/11]

**Applied:** torch.cuda.memory_allocated() with threading.Thread for background polling

### API Signatures

```python
class GPUMonitor:
    def __init__(self, poll_interval: float = 0.1):
        """Initialize GPU monitor with polling interval."""
        self.poll_interval = poll_interval
        self.memory_log = []
        self.monitoring = False
    
    def start_monitoring(self):
        """Start background thread to poll GPU memory every 0.1 sec."""
        ...
    
    def stop_monitoring(self) -> dict:
        """
        Stop monitoring and return results.
        
        Returns:
            {
                'max_gpu_memory_mb': float,
                'memory_log': pd.DataFrame,  # [timestamp, gpu_memory_mb]
                'cpu_only_verified': bool
            }
        """
        ...
    
    def _poll_gpu_memory(self):
        """Background thread function: continuously poll torch.cuda.memory_allocated()."""
        ...
    
    def save_memory_log(self, output_path: str):
        """Save memory log to CSV."""
        ...
```

### Pseudo-code

```
1. Start monitoring:
   self.monitoring = True
   thread = Thread(target=self._poll_gpu_memory)
   thread.start()

2. Polling loop (in background thread):
   while self.monitoring:
       if torch.cuda.is_available():
           memory_mb = torch.cuda.memory_allocated() / 1e6
       else:
           memory_mb = 0.0
       
       timestamp = time.time() - start_time
       self.memory_log.append({'timestamp': timestamp, 'gpu_memory_mb': memory_mb})
       time.sleep(self.poll_interval)

3. Stop monitoring:
   self.monitoring = False
   thread.join()
   
4. Compute max GPU usage:
   max_gpu_memory_mb = max(log['gpu_memory_mb'] for log in self.memory_log)
   cpu_only_verified = (max_gpu_memory_mb == 0.0)

5. Return results dict with DataFrame
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Thread setup | Create background Thread for polling |
| L-4-2 | GPU polling | torch.cuda.memory_allocated() / 1e6 |
| L-4-3 | Timestamp tracking | time.time() for each poll |
| L-4-4 | Max computation | Extract max from memory_log |
| L-4-5 | Verification | Check max == 0.0 |
| L-4-6 | CSV export | Save memory log to file |

---

## A-5: FeatureValidator [Complexity: 10, Budget: 10/10]

**Applied:** NumPy cosine similarity computation with pandas DataFrame comparison

### API Signatures

```python
class FeatureValidator:
    def __init__(self, cached_features_path: str):
        """Initialize validator with path to h-e1 cached features."""
        self.cached_features_path = cached_features_path
    
    def validate_equivalence(self, checkpoint_features: pd.DataFrame) -> dict:
        """
        Compare checkpoint-only features against h-e1 cached features.
        
        Args:
            checkpoint_features: Features from CheckpointOnlyExtractor
        
        Returns:
            {
                'overall_match': bool,
                'cosine_similarity': float,
                'per_model_similarity': dict[str, float],
                'mismatches': list[dict],
                'mismatch_rate': float
            }
        """
        ...
    
    def _compute_cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity: dot(v1, v2) / (norm(v1) * norm(v2))"""
        ...
    
    def _find_mismatches(self, cached_df: pd.DataFrame, checkpoint_df: pd.DataFrame) -> list:
        """Identify models with feature differences."""
        ...
    
    def save_validation_report(self, results: dict, output_path: str):
        """Save validation results to JSON."""
        ...
```

### Pseudo-code

```
1. Load cached features:
   cached_df = pd.read_csv(self.cached_features_path)

2. For each model in checkpoint_features:
   cached_row = cached_df[cached_df.model_name == model_name]
   checkpoint_row = checkpoint_features[checkpoint_features.model_name == model_name]
   
   # Extract feature vectors [bn, ln, gn, no_norm, R]
   cached_vec = cached_row[['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']].values
   checkpoint_vec = checkpoint_row[...].values
   
   # Compute cosine similarity
   similarity = self._compute_cosine_similarity(cached_vec, checkpoint_vec)
   per_model_similarity[model_name] = similarity

3. Overall similarity = mean(per_model_similarity.values())
4. Overall match = (overall_similarity == 1.0)
5. Detect mismatches where similarity < 1.0
6. Return results dict
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | CSV loading | Load h-e1 cached features |
| L-5-2 | Feature alignment | Match models by name |
| L-5-3 | Cosine similarity | NumPy dot product / norm |
| L-5-4 | Mismatch detection | Filter similarity < 1.0 |
| L-5-5 | Rate computation | mismatches / total_models |
| L-5-6 | JSON export | Save validation report |

---

## A-6: ScalabilityAnalyzer [Complexity: 9, Budget: 9/9]

**Applied:** NumPy linear regression with extrapolation

### API Signatures

```python
class ScalabilityAnalyzer:
    def __init__(self):
        """Initialize scalability analyzer."""
        ...
    
    def extrapolate_scaling(self, timing_results: dict, target_sizes: list[int]) -> dict:
        """
        Extrapolate linear scaling to larger model counts.
        
        Args:
            timing_results: From TimingBenchmark
            target_sizes: [100, 200, 500]
        
        Returns:
            {
                'linear_fit': dict,  # slope, intercept
                'extrapolations': dict[int, float],  # {100: 914.0, 200: 1828.0}
                'bottleneck_analysis': dict
            }
        """
        ...
    
    def identify_bottlenecks(self, per_model_times: dict) -> dict:
        """
        Identify slowest/fastest models.
        
        Returns:
            {
                'slowest_models': list[tuple],  # [(name, time), ...]
                'fastest_models': list[tuple],
                'time_by_family': dict[str, float]
            }
        """
        ...
    
    def save_scalability_report(self, results: dict, output_path: str):
        """Save scalability analysis to JSON."""
        ...
```

### Pseudo-code

```
1. Linear fit:
   avg_time_per_model = timing_results['avg_time']
   slope = avg_time_per_model
   intercept = 0.0

2. Extrapolate:
   for target_size in target_sizes:
       extrapolations[target_size] = slope * target_size

3. Bottleneck analysis:
   per_model_times = timing_results['per_model']
   slowest_models = sorted(per_model_times.items(), key=lambda x: x[1], reverse=True)[:5]
   fastest_models = sorted(per_model_times.items(), key=lambda x: x[1])[:5]

4. Return results dict
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Linear fit | slope = avg_time |
| L-6-2 | Extrapolation | time = slope * N |
| L-6-3 | Bottleneck sort | Sort per_model_times |
| L-6-4 | Family grouping | Group by CNN/Transformer/Hybrid |
| L-6-5 | JSON export | Save scalability report |

---

## A-7: GateEvaluator [Complexity: 8, Budget: 8/8]

**Applied:** Decision tree logic for MUST_WORK gate with threshold checks

### API Signatures

```python
class GateEvaluator:
    def __init__(self, thresholds: dict):
        """Initialize with gate thresholds."""
        self.thresholds = thresholds
    
    def evaluate_gate(self, 
                     timing_results: dict, 
                     gpu_results: dict, 
                     validation_results: dict) -> dict:
        """
        Evaluate MUST_WORK gate decision.
        
        Args:
            timing_results: From TimingBenchmark
            gpu_results: From GPUMonitor
            validation_results: From FeatureValidator
        
        Returns:
            {
                'gate_decision': str,  # 'PASS' or 'FAIL'
                'p1_passed': bool,  # total_time < 600
                'p2_passed': bool,  # gpu_memory == 0
                's1_passed': bool,  # feature_equivalence == 1.0
                's2_passed': bool,  # speedup > 3.0
                'failure_reasons': list[str],
                'recommendation': str
            }
        """
        ...
    
    def save_decision(self, decision: dict, output_path: str):
        """Save gate decision to JSON and TXT."""
        ...
```

### Pseudo-code

```
1. Extract criteria results:
   p1_passed = (timing_results['total_time'] < self.thresholds['total_time_max_seconds'])
   p2_passed = (gpu_results['max_gpu_memory_mb'] == 0)
   s1_passed = (validation_results['overall_match'] == True)
   s2_passed = (timing_results['speedup_factor'] > self.thresholds['speedup_min_factor'])

2. Gate decision logic:
   IF p1_passed AND p2_passed AND s1_passed AND s2_passed:
       gate_decision = 'PASS'
       recommendation = 'Proceed to H-C1'
   ELSE:
       gate_decision = 'FAIL'
       failure_reasons = []
       IF NOT p1_passed:
           failure_reasons.append(f"Extraction time {timing_results['total_time']:.1f}s exceeds 600s")
       IF NOT p2_passed:
           failure_reasons.append(f"GPU memory {gpu_results['max_gpu_memory_mb']:.1f}MB > 0MB")
       IF NOT s1_passed:
           failure_reasons.append(f"Feature equivalence failed")
       IF NOT s2_passed:
           failure_reasons.append(f"Speedup {timing_results['speedup_factor']:.1f}x < 3.0x")
       
       recommendation = 'EXPLORE parallel extraction or relax thresholds'

3. Return decision dict
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Criteria extraction | Get p1, p2, s1, s2 values |
| L-7-2 | Decision tree | Implement PASS/FAIL logic |
| L-7-3 | Failure reasons | Generate failure messages |
| L-7-4 | Recommendations | Generate next steps |
| L-7-5 | JSON/TXT export | Save decision to files |

---

## A-8: H_M3_Runner [Complexity: 16, Budget: 16/16]

**Applied:** Pipeline orchestration with 9-step protocol

### API Signatures

```python
class H_M3_Runner:
    def __init__(self, base_dir: str = None):
        """Initialize runner with base directory."""
        self.base_dir = base_dir or 'docs/youra_research/h-m3'
        self.h_m1_dir = 'docs/youra_research/h-m1'
    
    def run_mechanism_validation(self) -> dict:
        """
        Orchestrate 9-step checkpoint extraction validation protocol.
        
        Returns:
            {
                'checkpoint_timing': dict,
                'forward_timing': dict,
                'gpu_monitoring': dict,
                'feature_validation': dict,
                'scalability': dict,
                'gate_decision': dict,
                'total_runtime': float
            }
        """
        ...
    
    def _run_warmup(self):
        """Extract 1 model to warm up cache."""
        ...
    
    def _run_checkpoint_extraction(self) -> tuple:
        """Run CheckpointOnlyExtractor with timing. Returns (timing, features)."""
        ...
    
    def _run_forward_baseline(self) -> dict:
        """Run ForwardPassExtractor on 5-model subset. Returns timing dict."""
        ...
    
    def _generate_validation_report(self, results: dict, output_path: str):
        """Generate 04_validation.md report."""
        ...
    
    def _save_all_outputs(self, results: dict):
        """Save all JSON/CSV/PNG/TXT files."""
        ...
```

### Pseudo-code

```
1. Start timer:
   start_time = time.time()

2. Step 1 - Warmup:
   self._run_warmup()

3. Step 2 - Checkpoint-only extraction (50 models):
   gpu_monitor = GPUMonitor()
   gpu_monitor.start_monitoring()
   
   checkpoint_extractor = CheckpointOnlyExtractor()
   checkpoint_timing, checkpoint_features = self._run_checkpoint_extraction()
   
   gpu_results = gpu_monitor.stop_monitoring()

4. Step 3 - Forward-pass baseline (5 models):
   forward_extractor = ForwardPassExtractor()
   forward_timing = self._run_forward_baseline()

5. Step 4 - Timing benchmark:
   benchmark = TimingBenchmark()
   speedup_results = benchmark.compare_methods(checkpoint_timing, forward_timing)
   benchmark.plot_timing_comparison(speedup_results, f"{self.base_dir}/results/timing_comparison.png")

6. Step 5 - Feature validation:
   validator = FeatureValidator(f"{self.h_m1_dir}/code/data/train_features.csv")
   validation_results = validator.validate_equivalence(checkpoint_features)

7. Step 6 - Scalability analysis:
   analyzer = ScalabilityAnalyzer()
   scalability_results = analyzer.extrapolate_scaling(checkpoint_timing, [100, 200, 500])

8. Step 7 - Gate evaluation:
   gate_evaluator = GateEvaluator(thresholds=THRESHOLDS)
   gate_decision = gate_evaluator.evaluate_gate(
       checkpoint_timing, gpu_results, validation_results
   )

9. Step 8 - Save outputs:
   self._save_all_outputs({
       'checkpoint_timing': checkpoint_timing,
       'forward_timing': forward_timing,
       'gpu_monitoring': gpu_results,
       'feature_validation': validation_results,
       'scalability': scalability_results,
       'gate_decision': gate_decision
   })

10. Step 9 - Generate report:
    self._generate_validation_report(results, f"{self.base_dir}/04_validation.md")

11. End timer:
    total_runtime = time.time() - start_time

12. Return results
```

### Subtasks [16/16 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Warmup | Run 1-model extraction |
| L-8-2 | Checkpoint extraction | Run CheckpointOnlyExtractor |
| L-8-3 | GPU monitoring | Start/stop GPUMonitor |
| L-8-4 | Forward baseline | Run ForwardPassExtractor |
| L-8-5 | Timing benchmark | Run TimingBenchmark |
| L-8-6 | Feature validation | Run FeatureValidator |
| L-8-7 | Scalability | Run ScalabilityAnalyzer |
| L-8-8 | Gate evaluation | Run GateEvaluator |
| L-8-9 | Output saving | Save 7 output files |
| L-8-10 | Report generation | Generate 04_validation.md |
| L-8-11 | Runtime tracking | Time entire pipeline |

---

## External Dependencies API (From h-m2)

### Verified from Actual Code

The following modules are reused from h-m2 validated codebase:

```python
# From: docs/youra_research/h-m2/code/src/feature_extractor.py (ACTUAL CODE)
class StatisticalFeatureExtractor:
    def extract_features(self, state_dict: dict) -> dict:
        """
        Extract normalization counts and parameter-mass ratio.
        
        Args:
            state_dict: PyTorch model state dictionary
        
        Returns:
            {
                'bn_count': int,
                'ln_count': int,
                'gn_count': int,
                'no_norm_flag': int,
                'param_mass_ratio': float
            }
        """
        ...
    
    def _compute_param_mass_ratio(self, state_dict: dict) -> float:
        """
        Compute R = conv_params / (conv_params + linear_params).
        
        Logic:
            - 4D tensors → conv weights
            - 2D tensors → linear weights
            - Exclude classification head keys
        """
        ...


# From: docs/youra_research/h-m2/code/config.py (ACTUAL CODE)
MODEL_FAMILIES = {
    'CNN': [...],  # 24 models
    'Transformer': [...],  # 22 models
    'Hybrid': [...]  # 12 models
}

NORM_PATTERNS = {
    'bn': r'bn|batch_norm|batchnorm',
    'ln': r'ln|layer_norm|layernorm',
    'gn': r'gn|group_norm|groupnorm'
}

HEAD_KEYWORDS = ['head', 'fc', 'classifier']

FEATURE_NAMES = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']
```

**Verified from:** `docs/youra_research/h-m2/code/` (actual implementation)

**Note:** h-m3 reuses feature extraction logic but measures timing/monitoring for checkpoint-only vs forward-pass access patterns.

---

## Data Schemas

### Input Schema (Model List)

**50 models from h-e1 cache:**
```
CNN (20): resnet18, resnet34, resnet50, efficientnet_b0, ...
Transformer (20): vit_base_patch16_224, deit_tiny_patch16_224, swin_tiny_patch4_window7_224, ...
Hybrid (10): mixer_b16_224, coatnet_0_rw_224, maxvit_tiny_tf_224, ...
```

### Output Schemas

**checkpoint_only_timings.json:**
```json
{
  "total_time": 456.78,
  "avg_time": 9.14,
  "median_time": 8.52,
  "p90_time": 12.34,
  "per_model": {
    "resnet18": 7.23,
    "vit_base_patch16_224": 10.45
  }
}
```

**forward_pass_timings.json:**
```json
{
  "total_time": 123.45,
  "avg_time": 24.69,
  "per_model": {
    "resnet50": 22.34,
    "vit_base_patch16_224": 28.91
  }
}
```

**speedup_analysis.json:**
```json
{
  "speedup_factor": 5.2,
  "checkpoint_time": 456.78,
  "forward_time": 2375.0,
  "per_model_speedup": {
    "resnet50": 4.8,
    "vit_base_patch16_224": 6.1
  }
}
```

**gpu_memory_log.csv:**
```
timestamp,gpu_memory_mb
0.0,0.0
0.1,0.0
0.2,0.0
```

**feature_validation.json:**
```json
{
  "overall_match": true,
  "cosine_similarity": 1.0,
  "per_model_similarity": {
    "resnet18": 1.0,
    "vit_base_patch16_224": 1.0
  },
  "mismatches": [],
  "mismatch_rate": 0.0
}
```

**scalability_analysis.json:**
```json
{
  "linear_fit": {
    "slope": 9.14,
    "intercept": 0.0
  },
  "extrapolations": {
    "100": 914.0,
    "200": 1828.0,
    "500": 4570.0
  },
  "bottleneck_analysis": {
    "slowest_models": [
      ["vit_large_patch16_224", 15.23],
      ["swin_base_patch4_window7_224", 13.45]
    ],
    "fastest_models": [
      ["mobilenetv2_100", 5.12],
      ["resnet18", 6.34]
    ]
  }
}
```

**gate_evaluation.json:**
```json
{
  "gate_decision": "PASS",
  "p1_passed": true,
  "p2_passed": true,
  "s1_passed": true,
  "s2_passed": true,
  "failure_reasons": [],
  "recommendation": "Proceed to H-C1"
}
```

---

## Gate Conditions (MUST_WORK Logic)

### Primary Criteria

**P1: Total extraction time <10 min**
```python
P1_passed = (total_time < 600)
```

**P2: GPU memory usage = 0 MB**
```python
P2_passed = (max_gpu_memory_mb == 0)
```

### Secondary Criteria

**S1: Feature equivalence = 1.0**
```python
S1_passed = (cosine_similarity == 1.0)
```

**S2: Speedup >3x**
```python
S2_passed = (speedup_factor > 3.0)
```

### Gate Decision Tree

```
IF P1 AND P2 AND S1 AND S2:
    gate_decision = 'PASS'
    recommendation = 'Proceed to H-C1'
ELSE:
    gate_decision = 'FAIL'
    IF NOT P1:
        recommendation = 'EXPLORE parallel extraction'
    ELIF NOT P2:
        recommendation = 'ABANDON (GPU required)'
    ELIF NOT S1:
        recommendation = 'FIX extraction bug'
    ELIF NOT S2:
        recommendation = 'DOCUMENT limitation'
```

---

## Configuration

### Thresholds

```python
THRESHOLDS = {
    'total_time_max_seconds': 600,
    'per_model_avg_max_seconds': 12,
    'gpu_memory_max_mb': 0,
    'speedup_min_factor': 3.0,
    'feature_equivalence_min': 1.0
}
```

### Baseline Subset (5 models)

```python
BASELINE_SUBSET = [
    'resnet50',
    'vit_base_patch16_224',
    'efficientnet_b0',
    'deit_small_patch16_224',
    'swin_tiny_patch4_window7_224'
]
```

---

## Error Handling

### Checkpoint Download Failure

```python
# In CheckpointOnlyExtractor._download_checkpoint
try:
    checkpoint_path = timm.models.hub.download_cached_file(...)
except Exception as e:
    failed_models.append(model_name)
    continue
```

### GPU Memory Leak Detection

```python
# In GPUMonitor.stop_monitoring
if max_gpu_memory_mb > 0:
    raise RuntimeError(f"GPU memory leak detected: {max_gpu_memory_mb:.1f}MB")
```

### Feature Mismatch Detection

```python
# In FeatureValidator.validate_equivalence
if not overall_match:
    raise ValueError(f"Feature mismatch detected: {mismatches}")
```

---

## Performance Requirements

### Runtime Budget

**Target:** ≤10 minutes total

**Breakdown:**
- Warmup (1 model): <30 sec
- Checkpoint-only extraction (50 models): <8 min
- Forward-pass baseline (5 models): <2 min
- Timing analysis: <30 sec
- Feature validation: <30 sec
- Report generation: <30 sec
- **Total: ~8-9 minutes**

### Memory Budget

**Target:** ≤8 GB peak RAM

**Profile:**
- Checkpoint file: ~500 MB max
- state_dict in RAM: ~1 GB max
- Feature storage: ~2 KB
- GPU monitoring: ~1 MB
- Matplotlib figures: ~5 MB
- **Peak RAM: ~2 GB**

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Total extraction time | <600 sec | time.perf_counter() |
| Per-model avg time | <12 sec | mean(per_model_times) |
| GPU memory usage | 0 MB | torch.cuda.memory_allocated() |
| Feature equivalence | 1.0 | cosine_similarity() |
| Speedup vs forward-pass | >3.0 | checkpoint_time / forward_time |
| 90th percentile time | <20 sec | np.percentile(times, 90) |

---

## Document Metadata

**Version:** 1.0  
**Last Updated:** 2026-07-11  
**Status:** APPROVED for Phase 4 Implementation  
**Estimated Implementation Time:** 10 hours  
**Estimated Runtime:** 8-9 minutes  
**Code Reuse:** 100% feature extraction from h-m2  
**New Code:** 8 modules, ~500 LOC  
**Total Complexity:** 95 (14 + 12 + 15 + 11 + 10 + 9 + 8 + 16)  
**Budget Used:** 95/10 subtasks (10 total budget from allocation)
