# Logic Design: H-C4 Version-Stable Contract Validation System

**Hypothesis ID:** h-c4  
**Document Type:** Logic Design  
**Phase:** 3 - Implementation Planning  
**Status:** READY FOR CODING  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: condition_hypothesis  
**Status**: Extends h-m1/h-m2 contract frameworks  
**Analyzed Paths**:
- docs/youra_research/h-m1/code/contracts/validator.py (@validate_structural, ShapeViolation, DtypeViolation)
- docs/youra_research/h-m2/code/contracts/validator.py (@validate_metamorphic, MetamorphicViolation)

**Relevant Symbols**: validate_structural, validate_metamorphic, ShapeViolation, DtypeViolation, MetamorphicViolation

**Critical Finding**: h-m1/h-m2 use decorator-based validation with probe-based forward passes. h-c4 injects these contracts into test scripts and measures false positive rate across library versions.

---

## KB Pattern Application

**Applied**: Conda environment isolation, AST-based decorator injection, Wilson score confidence intervals for FPR, semantic versioning violation patterns (MSR 2020, ICSE 2018)

---

## L-1: Environment Manager [Complexity: 15, Budget: 15]

### API Signatures

```python
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict
import subprocess


@dataclass
class Environment:
    """Isolated library environment."""
    name: str
    library: str  # "pytorch" | "transformers" | "numpy"
    version: str  # "2.1.0" | "4.35.0" | "1.24.0"
    python_path: str  # Path to Python interpreter in environment
    conda_prefix: Path  # Environment directory
    
    def run_script(self, script_path: Path, timeout: float = 30.0) -> 'ExecutionResult':
        """Execute Python script in this environment."""
        ...
    
    def install_package(self, package: str) -> None:
        """Install additional package (e.g., 'pytest')."""
        ...
    
    def export_spec(self) -> dict:
        """Export environment.yml for reproducibility."""
        ...


@dataclass
class ExecutionResult:
    """Result of script execution in isolated environment."""
    success: bool  # True if exit code 0
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    contract_violations: List[str]  # Parsed from stderr


class EnvironmentManager:
    """Manages isolated conda environments for version testing."""
    
    def __init__(self, base_path: Path = Path('.envs')):
        """Initialize manager. base_path: Root directory for all environments."""
        self.base_path = base_path
        self.environments: Dict[str, Environment] = {}
    
    def create_environment(self, library: str, version: str) -> Environment:
        """
        Create isolated conda environment for library version.
        
        Args:
            library: "pytorch" | "transformers" | "numpy"
            version: Semantic version string (e.g., "2.1.0")
        
        Returns:
            Environment object with isolated installation
        
        Raises:
            EnvironmentCreationError: If conda create fails
        """
        ...
    
    def get_environment(self, library: str, version: str) -> Optional[Environment]:
        """Retrieve existing environment or None."""
        ...
    
    def list_environments(self) -> List[Environment]:
        """List all created environments."""
        ...
    
    def cleanup_environment(self, env: Environment) -> None:
        """Remove conda environment and free disk space."""
        ...
```

### Pseudo-code

```
EnvironmentManager.create_environment(library, version):
    1. env_name = f"{library}-{version}"
    2. env_path = self.base_path / env_name
    3. if env_path.exists():
        return cached Environment
    
    4. # Create conda environment
    subprocess.run([
        "conda", "create", "-n", env_name, 
        "python=3.10", "-y"
    ])
    
    5. # Activate and install library
    conda_prefix = subprocess.check_output([
        "conda", "info", "--envs"
    ]).parse(env_name)
    
    python_path = conda_prefix / "bin" / "python"
    
    6. # Install target library version
    if library == "pytorch":
        subprocess.run([
            python_path, "-m", "pip", "install",
            f"torch=={version}", "--index-url", 
            "https://download.pytorch.org/whl/cpu"
        ])
    elif library == "transformers":
        subprocess.run([
            python_path, "-m", "pip", "install",
            f"transformers=={version}"
        ])
    elif library == "numpy":
        subprocess.run([
            python_path, "-m", "pip", "install",
            f"numpy=={version}"
        ])
    
    7. # Install contract framework (from h-m1/h-m2)
    subprocess.run([
        python_path, "-m", "pip", "install", "-e",
        "../h-m1/code"  # Editable install of contract library
    ])
    
    8. # Export environment spec
    subprocess.run([
        "conda", "env", "export", "-n", env_name,
        "-f", env_path / "environment.yml"
    ])
    
    9. env = Environment(
        name=env_name,
        library=library,
        version=version,
        python_path=str(python_path),
        conda_prefix=env_path
    )
    
    10. self.environments[f"{library}-{version}"] = env
    11. return env
```

### Tensor Shapes

**Input:** N/A (environment management, no tensors)

**Output:** Environment with isolated library installation

---

## L-2: Contract Injector [Complexity: 18, Budget: 18]

### API Signatures

```python
import ast
import astor
from typing import List, Optional


@dataclass
class ContractInjectionPoint:
    """Location for contract injection."""
    function_name: str
    class_name: Optional[str]  # None for module-level functions
    line_number: int
    contract_type: str  # "structural" | "metamorphic"


class DecoratorInjector:
    """Injects contract decorators into Python scripts via AST manipulation."""
    
    def find_injection_points(self, script: str) -> List[ContractInjectionPoint]:
        """
        Identify functions/methods for contract injection.
        
        Args:
            script: Python source code string
        
        Returns:
            List of injection points (nn.Module.forward, model.forward, etc.)
        
        Logic:
            1. Parse AST
            2. Find class definitions inheriting from nn.Module
            3. Find forward() methods
            4. Find functions with tensor operations (matmul, softmax)
            5. Return injection points with metadata
        """
        ...
    
    def inject_contracts(
        self, 
        script: str, 
        injection_points: List[ContractInjectionPoint],
        contract_type: str
    ) -> str:
        """
        Inject contract decorators into script.
        
        Args:
            script: Original Python source
            injection_points: Functions to decorate
            contract_type: "structural" | "metamorphic"
        
        Returns:
            Modified source with @validate_structural/@validate_metamorphic
        
        Raises:
            InjectionError: If AST parsing fails
        """
        ...
    
    def inject_structural_contracts(self, script: str) -> str:
        """Convenience: inject structural contracts (shape, dtype)."""
        ...
    
    def inject_metamorphic_contracts(self, script: str) -> str:
        """Convenience: inject metamorphic contracts (softmax, dropout)."""
        ...
```

### Pseudo-code

```
DecoratorInjector.find_injection_points(script):
    1. tree = ast.parse(script)
    2. injection_points = []
    
    3. # Visitor pattern to find nn.Module classes
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if inherits from nn.Module
            if "nn.Module" in [base.id for base in node.bases]:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name == "forward":
                            injection_points.append(
                                ContractInjectionPoint(
                                    function_name="forward",
                                    class_name=node.name,
                                    line_number=item.lineno,
                                    contract_type="structural"
                                )
                            )
    
    4. # Find tensor operations for metamorphic contracts
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if hasattr(node.func, 'attr'):
                if node.func.attr in ['softmax', 'dropout', 'layer_norm']:
                    # Find enclosing function
                    parent_func = find_parent_function(tree, node)
                    injection_points.append(
                        ContractInjectionPoint(
                            function_name=parent_func.name,
                            class_name=None,
                            line_number=parent_func.lineno,
                            contract_type="metamorphic"
                        )
                    )
    
    5. return injection_points


DecoratorInjector.inject_contracts(script, injection_points, contract_type):
    1. tree = ast.parse(script)
    
    2. # Add import at top
    import_node = ast.ImportFrom(
        module='contracts.validator',
        names=[
            ast.alias(name=f'validate_{contract_type}', asname=None)
        ],
        level=0
    )
    tree.body.insert(0, import_node)
    
    3. # Inject decorators
    for point in injection_points:
        if point.contract_type == contract_type:
            # Find function node at point.line_number
            func_node = find_function_at_line(tree, point.line_number)
            
            # Add decorator
            decorator_node = ast.Name(
                id=f'validate_{contract_type}',
                ctx=ast.Load()
            )
            func_node.decorator_list.append(decorator_node)
    
    4. # AST → source code
    modified_source = astor.to_source(tree)
    5. return modified_source
```

### Tensor Shapes

**Input:** N/A (AST manipulation, no tensors)

**Output:** Modified source code with contract decorators

---

## L-3: False Positive Detector [Complexity: 12, Budget: 12]

### API Signatures

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class FalsePositive:
    """Detected false positive instance."""
    script_id: str
    contract_id: str
    source_version: str
    target_version: str
    violation_message: str
    breakage_type: str  # "api_deprecation" | "behavioral_change" | "numerical_drift" | "unknown"
    timestamp: datetime


class FalsePositiveDetector:
    """Detects and categorizes false positives."""
    
    def detect_false_positive(
        self,
        baseline_result: ExecutionResult,
        target_result: ExecutionResult,
        script_id: str,
        source_version: str,
        target_version: str
    ) -> Optional[FalsePositive]:
        """
        Detect false positive: baseline passes, target fails on valid code.
        
        Args:
            baseline_result: Execution on source version
            target_result: Execution on target version
            script_id: Script identifier
            source_version: Baseline library version
            target_version: Updated library version
        
        Returns:
            FalsePositive if detected, else None
        
        Logic:
            if baseline.success and not target.success:
                if "contract violation" in target.stderr:
                    return FalsePositive(...)
            return None
        """
        ...
    
    def categorize_breakage(self, fp: FalsePositive) -> str:
        """
        Categorize false positive root cause via heuristics.
        
        Args:
            fp: False positive instance
        
        Returns:
            Breakage type: "api_deprecation" | "behavioral_change" | 
                          "numerical_drift" | "unknown"
        
        Heuristics:
            - "DeprecationWarning" in violation_message → api_deprecation
            - "dtype" or "shape" in violation_message → behavioral_change
            - "tolerance" or "rtol" or "atol" in violation_message → numerical_drift
            - else → unknown
        """
        ...
```

### Pseudo-code

```
FalsePositiveDetector.detect_false_positive(baseline, target, script_id, src_ver, tgt_ver):
    1. # Check for false positive: baseline pass, target fail
    if baseline.success and not target.success:
        2. # Parse stderr for contract violations
        if "contract violation" in target.stderr.lower() or \
           "ShapeViolation" in target.stderr or \
           "DtypeViolation" in target.stderr or \
           "MetamorphicViolation" in target.stderr:
            
            3. # Extract violation message
            violation_msg = extract_violation_message(target.stderr)
            
            4. # Categorize breakage type
            breakage_type = self.categorize_breakage_heuristic(violation_msg)
            
            5. fp = FalsePositive(
                script_id=script_id,
                contract_id=extract_contract_id(violation_msg),
                source_version=src_ver,
                target_version=tgt_ver,
                violation_message=violation_msg,
                breakage_type=breakage_type,
                timestamp=datetime.now()
            )
            
            6. return fp
    
    7. return None


FalsePositiveDetector.categorize_breakage(fp):
    1. msg_lower = fp.violation_message.lower()
    
    2. if "deprecationwarning" in msg_lower or \
       "removed in version" in msg_lower or \
       "no longer supported" in msg_lower:
        return "api_deprecation"
    
    3. elif "dtype" in msg_lower or "shape" in msg_lower or \
         "type mismatch" in msg_lower:
        return "behavioral_change"
    
    4. elif "tolerance" in msg_lower or "rtol" in msg_lower or \
         "atol" in msg_lower or "numerical" in msg_lower:
        return "numerical_drift"
    
    5. else:
        return "unknown"
```

### Tensor Shapes

**Input:** N/A (string parsing, no tensors)

**Output:** FalsePositive categorization

---

## L-4: FPR Calculator [Complexity: 10, Budget: 10]

### API Signatures

```python
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
from scipy.stats import beta


@dataclass
class FPRMetrics:
    """False positive rate metrics."""
    overall_fpr: float
    fpr_by_contract_type: Dict[str, float]  # {"structural": 1.8%, "metamorphic": 5.5%}
    fpr_by_library: Dict[str, float]  # {"pytorch": 2.5%, "transformers": 4.0%}
    fpr_by_version_distance: Dict[int, float]  # {1: 2.5%, 2: 4.5%}
    confidence_interval_95: Tuple[float, float]  # Wilson score interval


class FPRCalculator:
    """Computes false positive rate with stratification."""
    
    def compute_fpr(
        self,
        results: List[Tuple[ExecutionResult, ExecutionResult]],
        metadata: List[dict]
    ) -> FPRMetrics:
        """
        Compute false positive rate.
        
        Args:
            results: List of (baseline_result, target_result) pairs
            metadata: Script metadata (contract_type, library, version_distance)
        
        Returns:
            FPRMetrics with stratified FPR + 95% confidence interval
        
        Formula:
            FPR = (False Positives) / (True Negatives + False Positives)
            
            False Positive: baseline pass, target fail (contract violation)
            True Negative: baseline pass, target pass
        """
        ...
    
    def compute_confidence_interval(self, fpr: float, n: int) -> Tuple[float, float]:
        """
        Compute 95% confidence interval using Wilson score interval.
        
        Args:
            fpr: Observed false positive rate
            n: Sample size
        
        Returns:
            (lower_bound, upper_bound)
        
        Formula (Wilson score):
            z = 1.96 (95% CI)
            p_hat = fpr
            CI = (p_hat + z²/2n ± z*sqrt(p_hat(1-p_hat)/n + z²/4n²)) / (1 + z²/n)
        """
        ...
    
    def stratify_fpr(
        self, 
        fps: List[FalsePositive], 
        metadata: List[dict]
    ) -> Dict[str, Dict[str, float]]:
        """
        Stratify FPR by contract type, library, version distance.
        
        Returns:
            {
                "contract_type": {"structural": 1.8%, "metamorphic": 5.5%},
                "library": {"pytorch": 2.5%, "transformers": 4.0%},
                "version_distance": {1: 2.5%, 2: 4.5%}
            }
        """
        ...
```

### Pseudo-code

```
FPRCalculator.compute_fpr(results, metadata):
    1. false_positives = 0
    2. true_negatives = 0
    
    3. for (baseline, target), meta in zip(results, metadata):
        if baseline.success and not target.success:
            # False positive
            false_positives += 1
        elif baseline.success and target.success:
            # True negative
            true_negatives += 1
    
    4. overall_fpr = false_positives / (false_positives + true_negatives)
    
    5. # Stratify by contract type
    fpr_by_contract = {}
    for contract_type in ["structural", "metamorphic"]:
        fps_type = count_fps_where(metadata, "contract_type", contract_type)
        tns_type = count_tns_where(metadata, "contract_type", contract_type)
        fpr_by_contract[contract_type] = fps_type / (fps_type + tns_type)
    
    6. # Stratify by library
    fpr_by_library = {}
    for library in ["pytorch", "transformers", "numpy"]:
        fps_lib = count_fps_where(metadata, "library", library)
        tns_lib = count_tns_where(metadata, "library", library)
        fpr_by_library[library] = fps_lib / (fps_lib + tns_lib)
    
    7. # Stratify by version distance
    fpr_by_distance = {}
    for distance in [1, 2]:
        fps_dist = count_fps_where(metadata, "version_distance", distance)
        tns_dist = count_tns_where(metadata, "version_distance", distance)
        fpr_by_distance[distance] = fps_dist / (fps_dist + tns_dist)
    
    8. # 95% CI
    ci_95 = self.compute_confidence_interval(
        overall_fpr, 
        false_positives + true_negatives
    )
    
    9. return FPRMetrics(
        overall_fpr=overall_fpr,
        fpr_by_contract_type=fpr_by_contract,
        fpr_by_library=fpr_by_library,
        fpr_by_version_distance=fpr_by_distance,
        confidence_interval_95=ci_95
    )


FPRCalculator.compute_confidence_interval(fpr, n):
    1. z = 1.96  # 95% CI
    2. p_hat = fpr
    
    3. # Wilson score interval
    center = (p_hat + z**2 / (2*n)) / (1 + z**2 / n)
    margin = z * np.sqrt(p_hat*(1-p_hat)/n + z**2/(4*n**2)) / (1 + z**2 / n)
    
    4. lower = center - margin
    5. upper = center + margin
    
    6. return (max(0.0, lower), min(1.0, upper))
```

### Tensor Shapes

**Input:** N/A (statistical computation, no tensors)

**Output:** FPR metrics with confidence intervals

---

## L-5: Root Cause Analyzer [Complexity: 14, Budget: 14]

### API Signatures

```python
from pathlib import Path
from typing import Optional, List
import requests


@dataclass
class BreakageAnalysis:
    """Root cause analysis for false positive."""
    root_cause: str  # Free-text explanation
    release_note_url: Optional[str]
    api_changed: Optional[str]  # e.g., "torch.nn.functional.softmax"
    fix_recommendation: str


class RootCauseAnalyzer:
    """Analyzes false positives via release note cross-reference."""
    
    def __init__(self, release_notes_cache: Path = Path('.release_notes')):
        """Initialize analyzer. release_notes_cache: Local cache directory."""
        self.cache_dir = release_notes_cache
        self.cache_dir.mkdir(exist_ok=True)
    
    def analyze_breakage(self, fp: FalsePositive) -> BreakageAnalysis:
        """
        Cross-reference false positive with library release notes.
        
        Args:
            fp: False positive instance
        
        Returns:
            BreakageAnalysis with root cause and fix recommendation
        
        Logic:
            1. Fetch release notes for version transition
            2. Search for API mentioned in violation message
            3. Extract deprecation notices, behavioral changes
            4. Generate fix recommendation
        """
        ...
    
    def fetch_release_notes(
        self, 
        library: str, 
        source_version: str, 
        target_version: str
    ) -> str:
        """
        Fetch release notes from library documentation.
        
        Sources:
            - PyTorch: https://pytorch.org/docs/{target_version}/notes/
            - HuggingFace: https://github.com/huggingface/transformers/releases/tag/v{target_version}
            - NumPy: https://numpy.org/doc/{target_version}/release.html
        
        Returns:
            Release notes text (cached locally)
        """
        ...
    
    def extract_api_changes(self, release_notes: str, api_name: str) -> List[str]:
        """
        Extract mentions of API in release notes.
        
        Args:
            release_notes: Release notes text
            api_name: API name (e.g., "torch.nn.functional.softmax")
        
        Returns:
            List of relevant paragraphs mentioning API
        """
        ...
    
    def generate_fix_recommendation(
        self, 
        fp: FalsePositive, 
        changes: List[str]
    ) -> str:
        """
        Generate actionable fix recommendation.
        
        Examples:
            - "Update contract tolerance to 1e-5 (numerical drift in cuDNN)"
            - "Add version-aware logic: if torch.__version__ >= '2.2', update shape check"
            - "Replace deprecated API: use dim parameter in softmax()"
        """
        ...
```

### Pseudo-code

```
RootCauseAnalyzer.analyze_breakage(fp):
    1. # Fetch release notes
    release_notes = self.fetch_release_notes(
        fp.source_version.split("-")[0],  # "pytorch" from "pytorch-2.1.0"
        fp.source_version.split("-")[1],  # "2.1.0"
        fp.target_version.split("-")[1]   # "2.2.0"
    )
    
    2. # Extract API name from violation message
    api_name = extract_api_from_message(fp.violation_message)
    # e.g., "torch.nn.functional.softmax" from "Softmax sum violation"
    
    3. # Search release notes for API changes
    api_changes = self.extract_api_changes(release_notes, api_name)
    
    4. # Generate root cause explanation
    if api_changes:
        root_cause = f"API '{api_name}' changed in {fp.target_version}: " + api_changes[0]
        release_note_url = get_release_url(fp.target_version)
    else:
        root_cause = f"No documented change found for '{api_name}'"
        release_note_url = None
    
    5. # Generate fix recommendation
    fix_rec = self.generate_fix_recommendation(fp, api_changes)
    
    6. return BreakageAnalysis(
        root_cause=root_cause,
        release_note_url=release_note_url,
        api_changed=api_name,
        fix_recommendation=fix_rec
    )


RootCauseAnalyzer.fetch_release_notes(library, src_ver, tgt_ver):
    1. cache_file = self.cache_dir / f"{library}_{src_ver}_to_{tgt_ver}.txt"
    
    2. if cache_file.exists():
        return cache_file.read_text()
    
    3. # Construct URL
    if library == "pytorch":
        url = f"https://pytorch.org/docs/{tgt_ver}/notes/changelog.html"
    elif library == "transformers":
        url = f"https://github.com/huggingface/transformers/releases/tag/v{tgt_ver}"
    elif library == "numpy":
        url = f"https://numpy.org/doc/{tgt_ver}/release.html"
    
    4. # Fetch
    response = requests.get(url, timeout=10)
    release_notes = response.text
    
    5. # Cache
    cache_file.write_text(release_notes)
    
    6. return release_notes


RootCauseAnalyzer.generate_fix_recommendation(fp, changes):
    1. if fp.breakage_type == "numerical_drift":
        return "Update contract tolerance to 1e-5 (expected float32 drift)"
    
    2. elif fp.breakage_type == "api_deprecation":
        # Extract suggested alternative from release notes
        if "use X instead" in changes[0]:
            alternative = extract_alternative(changes[0])
            return f"Replace deprecated API with {alternative}"
        else:
            return "Add version-aware contract: if version >= X, skip check"
    
    3. elif fp.breakage_type == "behavioral_change":
        return "Update contract to match new behavior (e.g., shape, dtype defaults)"
    
    4. else:
        return "Manual review required (unknown breakage type)"
```

### Tensor Shapes

**Input:** N/A (text analysis, no tensors)

**Output:** Breakage analysis with fix recommendations

---

## L-6: Version Transition Benchmark Harness [Complexity: 20, Budget: 20]

### API Signatures

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
import pandas as pd


@dataclass
class BenchmarkConfig:
    """Configuration for version-transition benchmark."""
    libraries: List[Tuple[str, List[str]]]  # [("pytorch", ["2.1.0", "2.2.0", "2.3.0"]), ...]
    corpus_path: Path
    contract_types: List[str]  # ["structural", "metamorphic"]
    parallel_workers: int


@dataclass
class BenchmarkResults:
    """Aggregated benchmark results."""
    fpr_metrics: FPRMetrics
    false_positives: List[FalsePositive]
    stability_matrix: pd.DataFrame  # version_pair × contract_type FPR heatmap
    execution_time: float


class VersionTransitionBenchmark:
    """Main experiment harness."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.env_manager = EnvironmentManager()
        self.injector = DecoratorInjector()
        self.fp_detector = FalsePositiveDetector()
        self.fpr_calc = FPRCalculator()
        self.root_cause = RootCauseAnalyzer()
    
    def run(self) -> BenchmarkResults:
        """
        Main experiment loop.
        
        Workflow:
            1. Setup: Create all environments (13 total)
            2. Corpus: Load 1000 test scripts
            3. Injection: Annotate contracts (3000 contract instances)
            4. Baseline: Run on source versions
            5. Transition: Run on target versions (12 version pairs)
            6. Detection: Identify false positives
            7. Analysis: Compute FPR, categorize breakages
            8. Reporting: Generate validation report
        
        Returns:
            BenchmarkResults with FPR metrics, FP list, stability matrix
        """
        ...
    
    def setup_environments(self) -> Dict[str, Environment]:
        """Create isolated environments for all versions."""
        ...
    
    def load_corpus(self) -> List[Tuple[str, str]]:
        """Load test scripts. Returns [(script_id, script_path), ...]."""
        ...
    
    def inject_contracts_batch(self, scripts: List[str]) -> List[str]:
        """Inject contracts into scripts. Returns annotated scripts."""
        ...
    
    def run_baseline_phase(
        self, 
        scripts: List[str], 
        envs: Dict[str, Environment]
    ) -> Dict[str, ExecutionResult]:
        """Run scripts on baseline versions. Returns {script_id: result}."""
        ...
    
    def run_transition_phase(
        self, 
        scripts: List[str], 
        version_pairs: List[Tuple[str, str]],
        envs: Dict[str, Environment]
    ) -> Dict[str, ExecutionResult]:
        """Run scripts on version pairs. Returns {script_id_pair: result}."""
        ...
    
    def detect_false_positives(
        self, 
        baseline_results: Dict, 
        transition_results: Dict
    ) -> List[FalsePositive]:
        """Compare baseline vs transition results, detect FPs."""
        ...
    
    def analyze_results(
        self, 
        fps: List[FalsePositive], 
        all_results: List
    ) -> BenchmarkResults:
        """Compute FPR, stability matrix, root cause analysis."""
        ...
```

### Pseudo-code

```
VersionTransitionBenchmark.run():
    1. start_time = time.time()
    
    2. # Setup environments
    envs = self.setup_environments()
    # Returns: {"pytorch-2.1.0": Environment, "pytorch-2.2.0": Environment, ...}
    
    3. # Load corpus
    corpus = self.load_corpus()
    # Returns: [("script_001", "test_corpus/pytorch_hub/resnet18.py"), ...]
    
    4. # Inject contracts
    annotated_scripts = []
    for script_id, script_path in corpus:
        script_code = Path(script_path).read_text()
        annotated = self.injector.inject_structural_contracts(script_code)
        annotated_scripts.append((script_id, annotated))
    
    5. # Baseline phase: Run on source versions
    baseline_results = self.run_baseline_phase(annotated_scripts, envs)
    
    6. # Transition phase: Run on version pairs
    version_pairs = [
        ("pytorch-2.1.0", "pytorch-2.2.0"),
        ("pytorch-2.1.0", "pytorch-2.3.0"),
        ("pytorch-2.2.0", "pytorch-2.3.0"),
        ...
    ]
    transition_results = self.run_transition_phase(annotated_scripts, version_pairs, envs)
    
    7. # Detect false positives
    fps = self.detect_false_positives(baseline_results, transition_results)
    
    8. # Analyze results
    results = self.analyze_results(fps, baseline_results + transition_results)
    
    9. results.execution_time = time.time() - start_time
    10. return results


VersionTransitionBenchmark.run_baseline_phase(scripts, envs):
    1. baseline_results = {}
    
    2. for script_id, script_code in scripts:
        for version, env in envs.items():
            # Write script to temp file
            temp_path = Path(f"/tmp/{script_id}_{version}.py")
            temp_path.write_text(script_code)
            
            # Execute in environment
            result = env.run_script(temp_path, timeout=30.0)
            
            # Store result
            baseline_results[f"{script_id}_{version}"] = result
    
    3. return baseline_results


VersionTransitionBenchmark.detect_false_positives(baseline, transition):
    1. fps = []
    
    2. for (src_ver, tgt_ver) in version_pairs:
        for script_id in script_ids:
            baseline_key = f"{script_id}_{src_ver}"
            transition_key = f"{script_id}_{src_ver}→{tgt_ver}"
            
            baseline_res = baseline[baseline_key]
            transition_res = transition[transition_key]
            
            # Detect FP
            fp = self.fp_detector.detect_false_positive(
                baseline_res, transition_res,
                script_id, src_ver, tgt_ver
            )
            
            if fp:
                fps.append(fp)
    
    3. return fps
```

### Tensor Shapes

**Input:** Test corpus (1000 scripts), library versions (13 environments)

**Output:** BenchmarkResults with FPR metrics, FP list, stability matrix

---

## Implementation Order

### Phase 1: Environment Setup (2 days)
1. L-1: Environment Manager
2. Test: Create 13 environments, verify isolation

### Phase 2: Contract Injection (1 day)
3. L-2: Contract Injector
4. Test: Inject contracts into 10 sample scripts, verify AST correctness

### Phase 3: Execution Pipeline (2 days)
5. L-6: Version Transition Benchmark (setup, corpus, baseline, transition phases)
6. Test: Run mini benchmark (10 scripts, 2 version pairs)

### Phase 4: FP Detection & Analysis (2 days)
7. L-3: False Positive Detector
8. L-4: FPR Calculator
9. L-5: Root Cause Analyzer
10. Test: Detect FPs on sample results, compute FPR, generate root cause

### Phase 5: Full Benchmark Run (2 days)
11. Execute full benchmark (1000 scripts, 12 version pairs)
12. Generate validation report

**Total Budget:** 89 complexity units (15+18+12+10+14+20)  
**Allocated Budget:** 132 (from pipeline state)  
**Margin:** 43 units (33% buffer for debugging, edge cases)

---

**Logic Design Status:** APPROVED  
**Next Document:** Configuration Design (03_config.md)  
**Implementation Duration:** 1 week (9 days with parallelization)
