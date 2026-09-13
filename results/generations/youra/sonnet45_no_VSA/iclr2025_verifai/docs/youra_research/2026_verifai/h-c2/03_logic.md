# Core Logic Document: H-C2 Mutation Testing Validation

**Date:** 2026-07-11  
**Hypothesis:** Synthesized specifications achieve ≥70% mutation kill rate relative to gold specs  
**Phase:** Phase 3 - Logic Design  
**Budget:** 11 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-m1 base code  
**Analyzed Path:** `/workspace/TEST_verifai/docs/youra_research/h-m1/code/code/`  
**Relevant Symbols:**
- `IterativeRefinementLoop.synthesize_specification(c_code, temp_dir)` - Verified
- `FramaCVerifier.verify(acsl_spec, temp_dir)` - Verified
- `ACSLSpec` dataclass - Verified
- `VerificationResult` dataclass - Verified

**Critical Finding:** All base hypothesis APIs use exact parameter names from actual implementation. No spec-code divergence detected.

---

## Knowledge Base Research (Archon)

**Applied:** Standard mutation testing framework pattern, AST-based transformation patterns

---

## Task Allocation Reference

From `03_architecture.md`:
- **C-1**: Mutation Operators (Complexity: 14, Budget: 2 subtasks)
- **C-2**: Mutant Generator (Complexity: 11, Budget: 2 subtasks)
- **C-3**: Mutation Tester (Complexity: 13, Budget: 2 subtasks)
- **C-4**: Specification Synthesizer (Complexity: 7, Budget: 1 subtask)
- **C-5**: Dataset Loader (Complexity: 8, Budget: 1 subtask)
- **C-6**: Comparison Analyzer (Complexity: 12, Budget: 2 subtasks)
- **C-9**: Integration Runner (Complexity: 15, Budget: 1 subtask)

Total Budget: 11 subtasks (focused on high-complexity logic only)

---

## C-1: Mutation Operators [Complexity: 14, Budget: 2]

**Applied:** AST traversal and transformation patterns

### API Signatures

```python
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
import pycparser
from pycparser import c_ast

@dataclass
class Mutant:
    """Single mutant representation."""
    mutant_id: str
    original_code: str
    mutated_code: str
    operator_type: str
    location: dict  # {line, column, function}

class MutationOperator(ABC):
    """Base mutation operator."""
    
    @abstractmethod
    def apply(self, ast: c_ast.FileAST) -> List[Mutant]:
        """Generate mutants from AST. ast: pycparser AST -> List[Mutant]"""
        pass
    
    def get_operator_name(self) -> str:
        """Return operator name for tracking."""
        return self.__class__.__name__

class ArithmeticMutation(MutationOperator):
    """Mutate +/-, *//, ++/--"""
    
    def apply(self, ast: c_ast.FileAST) -> List[Mutant]:
        """
        Transform: + -> -, * -> /, ++ -> --
        Returns: List of mutated ASTs
        """
        pass

class RelationalMutation(MutationOperator):
    """Mutate </<=/>, >/>=/<, ==/!="""
    
    def apply(self, ast: c_ast.FileAST) -> List[Mutant]:
        """Transform relational operators."""
        pass

class BooleanMutation(MutationOperator):
    """Mutate &&/||, insert/delete !"""
    
    def apply(self, ast: c_ast.FileAST) -> List[Mutant]:
        """Transform boolean operators."""
        pass

class StatementMutation(MutationOperator):
    """Delete statements, change constants (±1)"""
    
    def apply(self, ast: c_ast.FileAST) -> List[Mutant]:
        """Delete or modify statements."""
        pass

class BoundaryMutation(MutationOperator):
    """Mutate array[i]->array[i±1], i<n->i<n±1"""
    
    def apply(self, ast: c_ast.FileAST) -> List[Mutant]:
        """Shift array bounds and loop conditions."""
        pass
```

### Pseudo-code (AST Mutation Algorithm)

```
ALGORITHM: Apply Mutation Operator

INPUT: C AST (pycparser.c_ast.FileAST), operator type
OUTPUT: List[Mutant]

1. Initialize mutants = []
2. Create AST visitor for target operator type:
   - ArithmeticMutation: visit BinaryOp nodes (+, -, *, /)
   - RelationalMutation: visit BinaryOp nodes (<, <=, >, >=, ==, !=)
   - BoundeanMutation: visit BinaryOp (&&, ||), UnaryOp (!)
   - StatementMutation: visit all statement nodes
   - BoundaryMutation: visit ArrayRef, For loop bounds

3. For each target node:
   a. Clone AST
   b. Replace node with mutated version:
      - ArithmeticMutation: + -> -, * -> /, ++ -> --
      - RelationalMutation: < -> <=, == -> !=
      - BooleanMutation: && -> ||, add/remove !
      - StatementMutation: delete node, change constant (5 -> 6)
      - BoundaryMutation: arr[i] -> arr[i+1], i<n -> i<n-1
   c. Generate C code from mutated AST (using CGenerator)
   d. Create Mutant object with metadata
   e. Add to mutants list

4. Return mutants
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | AST visitor logic | Traverse and identify mutation points |
| L-1-2 | Operator transformation | Clone and mutate AST nodes |

---

## C-2: Mutant Generator [Complexity: 11, Budget: 2]

**Applied:** AST parsing and compilability filtering

### API Signatures

```python
from typing import List
from pathlib import Path

class CASTParser:
    """Parse and validate C code using pycparser."""
    
    def __init__(self):
        self.parser = pycparser.CParser()
    
    def parse(self, c_code: str) -> pycparser.c_ast.FileAST:
        """
        Parse C code to AST.
        
        Args:
            c_code: C source code string
        
        Returns:
            pycparser AST
        """
        pass
    
    def unparse(self, ast: pycparser.c_ast.FileAST) -> str:
        """Generate C code from AST. ast -> C code string"""
        from pycparser.c_generator import CGenerator
        generator = CGenerator()
        return generator.visit(ast)
    
    def check_compilability(self, c_code: str) -> bool:
        """
        Check if code compiles with gcc.
        
        Args:
            c_code: C source code
        
        Returns:
            True if compiles, False otherwise
        """
        import subprocess
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.c', delete=False) as f:
            f.write(c_code.encode())
            f.flush()
            
            result = subprocess.run(
                ['gcc', '-c', f.name, '-o', '/dev/null'],
                capture_output=True
            )
            return result.returncode == 0

class MutantGenerator:
    """Generate and filter mutants from C programs."""
    
    def __init__(self, operators: List[MutationOperator]):
        """
        Args:
            operators: List of mutation operators to apply
        """
        self.operators = operators
        self.parser = CASTParser()
    
    def generate_mutants(self, c_program: str) -> List[Mutant]:
        """
        Generate all mutants from C program.
        
        Args:
            c_program: Original C code
        
        Returns:
            List of compilable mutants
        """
        ast = self.parser.parse(c_program)
        all_mutants = []
        
        for operator in self.operators:
            mutants = operator.apply(ast)
            all_mutants.extend(mutants)
        
        # Filter compilable only
        return self.filter_compilable(all_mutants)
    
    def filter_compilable(self, mutants: List[Mutant]) -> List[Mutant]:
        """Remove non-compilable mutants. Returns: filtered list"""
        compilable = []
        for mutant in mutants:
            if self.parser.check_compilability(mutant.mutated_code):
                compilable.append(mutant)
        return compilable
    
    def count_by_operator(self, mutants: List[Mutant]) -> dict:
        """Compute mutant counts per operator. Returns: {operator -> count}"""
        from collections import Counter
        return Counter(m.operator_type for m in mutants)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | AST parsing | Parse C code to pycparser AST |
| L-2-2 | Compilability filter | gcc compilation check |

---

## C-3: Mutation Tester [Complexity: 13, Budget: 2]

**Applied:** Parallel verification pattern with timeout handling

### API Signatures

```python
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from multiprocessing import Pool
import subprocess

@dataclass
class MutationTestResult:
    """Result of testing one mutant."""
    mutant_id: str
    killed: bool
    verification_status: str  # "FAILED", "PASSED", "TIMEOUT"
    timeout: bool
    error: Optional[str]

@dataclass
class KillRateResult:
    """Aggregated kill rate for one program."""
    program_id: str
    spec_type: str  # "synthesized" or "gold"
    total_mutants: int
    killed: int
    survived: int
    timeout_count: int
    kill_rate: float  # killed / (total - timeout) * 100
    operator_breakdown: dict  # {operator -> kill_rate}

class MutationTester:
    """Execute mutants with Frama-C verification."""
    
    def __init__(self, verifier, timeout: int = 10):
        """
        Args:
            verifier: FramaCVerifier instance from h-m1
            timeout: Per-mutant timeout in seconds
        """
        self.verifier = verifier
        self.timeout = timeout
    
    def test_mutant(
        self,
        mutant: Mutant,
        acsl_spec: 'ACSLSpec',
        temp_dir: Path
    ) -> MutationTestResult:
        """
        Test if specification detects mutant.
        
        Args:
            mutant: Mutated code
            acsl_spec: ACSL specification to test
            temp_dir: Working directory
        
        Returns:
            MutationTestResult (killed if verification fails)
        
        Logic:
        1. Insert ACSL annotations from spec into mutant code
        2. Run Frama-C/WP verification (timeout=10s)
        3. killed = (verification status == "FAILED")
           - If mutant causes failed proof -> spec detected bug -> killed
           - If mutant still verifies -> spec missed bug -> survived
        """
        try:
            # Insert ACSL spec into mutant
            annotated_mutant = self._insert_acsl_spec(mutant.mutated_code, acsl_spec)
            
            # Create temp ACSLSpec object
            from h_m1.code.code.src.llm_client import ACSLSpec as BaseACSLSpec
            mutant_spec = BaseACSLSpec(
                annotated_code=annotated_mutant,
                preconditions=acsl_spec.preconditions,
                postconditions=acsl_spec.postconditions,
                loop_invariants=acsl_spec.loop_invariants,
                assertions=acsl_spec.assertions
            )
            
            # Verify with Frama-C
            result = self.verifier.verify(mutant_spec, temp_dir)
            
            # Killed if verification failed (spec detected bug)
            killed = (result.proved_obligations < result.total_obligations)
            
            return MutationTestResult(
                mutant_id=mutant.mutant_id,
                killed=killed,
                verification_status="FAILED" if killed else "PASSED",
                timeout=False,
                error=None
            )
            
        except subprocess.TimeoutExpired:
            return MutationTestResult(
                mutant_id=mutant.mutant_id,
                killed=False,
                verification_status="TIMEOUT",
                timeout=True,
                error="Verification timeout"
            )
    
    def compute_kill_rate(
        self,
        program_id: str,
        mutants: List[Mutant],
        spec: 'ACSLSpec',
        spec_type: str,
        temp_dir: Path
    ) -> KillRateResult:
        """
        Compute kill rate for all mutants.
        
        Args:
            program_id: Program identifier
            mutants: List of mutants
            spec: ACSL specification
            spec_type: "synthesized" or "gold"
            temp_dir: Working directory
        
        Returns:
            KillRateResult with statistics
        """
        results = self.run_parallel(mutants, spec, temp_dir, workers=4)
        
        killed_count = sum(1 for r in results if r.killed)
        timeout_count = sum(1 for r in results if r.timeout)
        valid_count = len(results) - timeout_count
        survived_count = valid_count - killed_count
        
        kill_rate = (killed_count / valid_count * 100) if valid_count > 0 else 0.0
        
        # Per-operator breakdown
        operator_breakdown = self._compute_operator_breakdown(mutants, results)
        
        return KillRateResult(
            program_id=program_id,
            spec_type=spec_type,
            total_mutants=len(mutants),
            killed=killed_count,
            survived=survived_count,
            timeout_count=timeout_count,
            kill_rate=kill_rate,
            operator_breakdown=operator_breakdown
        )
    
    def run_parallel(
        self,
        mutants: List[Mutant],
        spec: 'ACSLSpec',
        temp_dir: Path,
        workers: int = 4
    ) -> List[MutationTestResult]:
        """Parallel mutant verification. Returns: List of results"""
        with Pool(workers) as pool:
            args = [(m, spec, temp_dir) for m in mutants]
            results = pool.starmap(self.test_mutant, args)
        return results
    
    def _insert_acsl_spec(self, c_code: str, acsl_spec: 'ACSLSpec') -> str:
        """Insert ACSL annotations from spec into code."""
        # Parse spec's annotated_code to extract ACSL comments
        # Insert into mutant at corresponding locations
        pass
    
    def _compute_operator_breakdown(
        self,
        mutants: List[Mutant],
        results: List[MutationTestResult]
    ) -> dict:
        """Compute kill rate per operator type."""
        from collections import defaultdict
        
        operator_stats = defaultdict(lambda: {"killed": 0, "total": 0})
        
        for mutant, result in zip(mutants, results):
            if not result.timeout:
                operator_stats[mutant.operator_type]["total"] += 1
                if result.killed:
                    operator_stats[mutant.operator_type]["killed"] += 1
        
        return {
            op: stats["killed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            for op, stats in operator_stats.items()
        }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Mutant verification | Integrate Frama-C verification |
| L-3-2 | Kill rate aggregation | Compute statistics per program |

---

## C-4: Specification Synthesizer [Complexity: 7, Budget: 1]

**Applied:** Wrapper pattern over h-m1 refinement loop

### API Signatures

```python
from pathlib import Path
from h_m1.code.code.src.refinement_loop import IterativeRefinementLoop
from h_m1.code.code.src.llm_client import ACSLSpec

class SpecificationSynthesizer:
    """Wrapper for h-m1 synthesis mechanism."""
    
    def __init__(
        self,
        llm_client,
        verifier,
        feedback_extractor
    ):
        """
        Args:
            llm_client: SpecificationGenerator from h-m1
            verifier: FramaCVerifier from h-m1
            feedback_extractor: FeedbackExtractor from h-m1
        """
        self.refinement_loop = IterativeRefinementLoop(
            generator=llm_client,
            verifier=verifier,
            feedback_extractor=feedback_extractor,
            max_iterations=10,
            no_improvement_threshold=3
        )
    
    def synthesize_with_feedback(
        self,
        c_program: str,
        temp_dir: Path
    ) -> ACSLSpec:
        """
        Synthesize ACSL spec using FullStructured feedback (h-m1 validated).
        
        Args:
            c_program: Unannotated C code
            temp_dir: Working directory
        
        Returns:
            ACSLSpec with synthesized annotations
        """
        history = self.refinement_loop.synthesize_specification(c_program, temp_dir)
        return history.final_spec
    
    def get_synthesis_metrics(self) -> dict:
        """Extract synthesis metrics. Returns: {iterations, discharge_rate, ...}"""
        pass
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | h-m1 integration | Wrap refinement loop |

---

## C-5: Dataset Loader [Complexity: 8, Budget: 1]

**Applied:** Git clone and stratified sampling patterns

### API Signatures

```python
from dataclasses import dataclass
from typing import List
from pathlib import Path
import subprocess
import yaml

@dataclass
class Program:
    """Single program with gold spec."""
    program_id: str
    c_code: str
    gold_spec: 'ACSLSpec'
    loc: int
    function_count: int
    complexity: str  # "simple", "medium", "complex"
    file_path: str

class ACSLByExampleLoader:
    """Load ACSL-by-Example benchmark."""
    
    def __init__(self, repo_path: str):
        """
        Args:
            repo_path: Path to clone repository
        """
        self.repo_path = Path(repo_path)
    
    def load_programs(
        self,
        num_programs: int = 30,
        stratified: bool = True
    ) -> List[Program]:
        """
        Load programs from ACSL-by-Example.
        
        Args:
            num_programs: Number to load
            stratified: Sample across complexity levels
        
        Returns:
            List of Program objects
        
        Logic:
        1. Clone repo: git clone https://github.com/fraunhoferfokus/acsl-by-example
        2. Parse C files with ACSL annotations
        3. Stratified sampling: 10 simple, 15 medium, 5 complex
        4. Extract gold specs from ACSL comments
        """
        if not self.repo_path.exists():
            self._clone_repo()
        
        all_programs = self._discover_programs()
        
        if stratified:
            return self._stratified_sample(all_programs, num_programs)
        else:
            return all_programs[:num_programs]
    
    def get_program_metadata(self, program: Program) -> dict:
        """Extract metadata. Returns: {loc, functions, obligations}"""
        pass
    
    def validate_gold_spec(self, program: Program) -> bool:
        """Verify gold spec compiles with Frama-C."""
        pass
    
    def _clone_repo(self):
        """Clone ACSL-by-Example repository."""
        subprocess.run([
            'git', 'clone',
            'https://github.com/fraunhoferfokus/acsl-by-example',
            str(self.repo_path)
        ], check=True)
    
    def _discover_programs(self) -> List[Program]:
        """Find all C programs with ACSL specs."""
        pass
    
    def _stratified_sample(self, programs: List[Program], n: int) -> List[Program]:
        """Sample across complexity levels."""
        # Simple: LOC < 30
        # Medium: 30 <= LOC < 60
        # Complex: LOC >= 60
        pass
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Dataset parsing | Clone and parse ACSL-annotated C files |

---

## C-6: Comparison Analyzer [Complexity: 12, Budget: 2]

**Applied:** Statistical comparison and gate logic

### API Signatures

```python
from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class ComparisonResult:
    """Per-program comparison."""
    program_id: str
    synthesized_kill_rate: float
    gold_kill_rate: float
    relative_performance: float  # synthesized / gold
    synthesized_result: KillRateResult
    gold_result: KillRateResult

@dataclass
class GateDecision:
    """Final gate validation."""
    gate_passed: bool
    mean_synthesized: float
    mean_gold: float
    threshold: float  # 0.70 * mean_gold
    relative_performance: float  # mean_synthesized / mean_gold
    failing_programs: List[str]

class ComparisonAnalyzer:
    """Compare synthesized vs gold specifications."""
    
    def __init__(self, threshold: float = 0.70):
        """
        Args:
            threshold: Minimum relative performance (default: 0.70)
        """
        self.threshold = threshold
    
    def compare_specs(
        self,
        synthesized_results: List[KillRateResult],
        gold_results: List[KillRateResult]
    ) -> List[ComparisonResult]:
        """
        Compare kill rates per program.
        
        Args:
            synthesized_results: Results for synthesized specs
            gold_results: Results for gold specs
        
        Returns:
            List of ComparisonResult objects
        """
        comparisons = []
        
        for synth, gold in zip(synthesized_results, gold_results):
            assert synth.program_id == gold.program_id
            
            relative = synth.kill_rate / gold.kill_rate if gold.kill_rate > 0 else 0.0
            
            comparisons.append(ComparisonResult(
                program_id=synth.program_id,
                synthesized_kill_rate=synth.kill_rate,
                gold_kill_rate=gold.kill_rate,
                relative_performance=relative,
                synthesized_result=synth,
                gold_result=gold
            ))
        
        return comparisons
    
    def compute_gate_decision(
        self,
        comparisons: List[ComparisonResult]
    ) -> GateDecision:
        """
        Make gate decision: PASS if mean_synth >= 0.70 * mean_gold.
        
        Args:
            comparisons: Per-program comparisons
        
        Returns:
            GateDecision with verdict
        """
        synth_rates = [c.synthesized_kill_rate for c in comparisons]
        gold_rates = [c.gold_kill_rate for c in comparisons]
        
        mean_synth = np.mean(synth_rates)
        mean_gold = np.mean(gold_rates)
        
        threshold_value = self.threshold * mean_gold
        gate_passed = mean_synth >= threshold_value
        
        failing_programs = [
            c.program_id for c in comparisons
            if c.relative_performance < self.threshold
        ]
        
        return GateDecision(
            gate_passed=gate_passed,
            mean_synthesized=mean_synth,
            mean_gold=mean_gold,
            threshold=threshold_value,
            relative_performance=mean_synth / mean_gold if mean_gold > 0 else 0,
            failing_programs=failing_programs
        )
    
    def generate_statistics(self, comparisons: List[ComparisonResult]) -> dict:
        """Compute summary statistics. Returns: {mean, std, min, max, ...}"""
        synth_rates = [c.synthesized_kill_rate for c in comparisons]
        gold_rates = [c.gold_kill_rate for c in comparisons]
        
        return {
            "synthesized": {
                "mean": np.mean(synth_rates),
                "std": np.std(synth_rates),
                "min": np.min(synth_rates),
                "max": np.max(synth_rates)
            },
            "gold": {
                "mean": np.mean(gold_rates),
                "std": np.std(gold_rates),
                "min": np.min(gold_rates),
                "max": np.max(gold_rates)
            },
            "correlation": np.corrcoef(synth_rates, gold_rates)[0, 1]
        }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Kill rate comparison | Per-program relative performance |
| L-6-2 | Gate decision logic | Threshold-based validation |

---

## C-9: Integration Runner [Complexity: 15, Budget: 1]

**Applied:** Pipeline orchestration with checkpointing

### API Signatures

```python
from pathlib import Path
from typing import List
import yaml
import json

class MutationExperimentRunner:
    """End-to-end mutation testing pipeline."""
    
    def __init__(self, config_path: str):
        """
        Args:
            config_path: Path to mutation_config.yaml
        """
        self.config = self._load_config(config_path)
        self.components = {}
        self.checkpoint_dir = Path(self.config['output']['results_dir']) / 'checkpoints'
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self):
        """
        Execute full pipeline.
        
        Pipeline:
        1. Load dataset (30 programs)
        2. Synthesize specifications (resume from checkpoint)
        3. Generate mutants per program
        4. Run mutation testing (synthesized + gold)
        5. Analyze and compare results
        6. Generate figures and report
        
        Returns:
            GateDecision
        """
        # 1. Setup
        self._setup_components()
        
        # 2. Load dataset
        programs = self._load_dataset()
        
        # 3. Synthesize specs (with checkpointing)
        synthesized_specs = self._synthesize_specifications(programs)
        
        # 4. Run mutation testing
        synthesized_results, gold_results = self._run_mutation_testing(
            programs, synthesized_specs
        )
        
        # 5. Analyze
        gate_decision = self._analyze_results(synthesized_results, gold_results)
        
        # 6. Generate outputs
        self._generate_outputs(gate_decision, synthesized_results, gold_results)
        
        return gate_decision
    
    def _setup_components(self):
        """Initialize all components from config."""
        from h_m1.code.code.src.llm_client import SpecificationGenerator
        from h_m1.code.code.src.verifier import FramaCVerifier
        from h_m1.code.code.src.feedback_parser import FeedbackExtractor
        
        # Initialize h-m1 components
        self.components['generator'] = SpecificationGenerator(
            api_key=self.config['synthesis']['api_key_env'],
            model=self.config['synthesis']['llm_model']
        )
        self.components['verifier'] = FramaCVerifier(
            timeout_per_obligation=self.config['verification']['timeout_seconds']
        )
        self.components['feedback_extractor'] = FeedbackExtractor()
        
        # Initialize h-c2 components
        self.components['synthesizer'] = SpecificationSynthesizer(
            self.components['generator'],
            self.components['verifier'],
            self.components['feedback_extractor']
        )
        
        # Mutation components
        operators = self._create_mutation_operators()
        self.components['mutant_generator'] = MutantGenerator(operators)
        self.components['mutation_tester'] = MutationTester(
            self.components['verifier'],
            timeout=self.config['verification']['timeout_seconds']
        )
        
        # Analysis
        self.components['analyzer'] = ComparisonAnalyzer(
            threshold=self.config['comparison']['gate_threshold']
        )
    
    def _load_dataset(self) -> List[Program]:
        """Load ACSL-by-Example programs."""
        loader = ACSLByExampleLoader(self.config['dataset']['repo_path'])
        return loader.load_programs(
            num_programs=self.config['dataset']['num_programs'],
            stratified=self.config['dataset']['stratified_sampling']
        )
    
    def _synthesize_specifications(self, programs: List[Program]) -> List['ACSLSpec']:
        """Synthesize specs with checkpoint recovery."""
        checkpoint_file = self.checkpoint_dir / 'synthesized_specs.json'
        
        if checkpoint_file.exists():
            with checkpoint_file.open() as f:
                checkpoint = json.load(f)
            completed_ids = set(checkpoint.keys())
        else:
            checkpoint = {}
            completed_ids = set()
        
        synthesized = []
        for program in programs:
            if program.program_id in completed_ids:
                # Load from checkpoint
                spec_data = checkpoint[program.program_id]
                synthesized.append(self._deserialize_spec(spec_data))
            else:
                # Synthesize new
                spec = self.components['synthesizer'].synthesize_with_feedback(
                    program.c_code,
                    Path('/tmp/mutation_test')
                )
                synthesized.append(spec)
                
                # Save checkpoint
                checkpoint[program.program_id] = self._serialize_spec(spec)
                with checkpoint_file.open('w') as f:
                    json.dump(checkpoint, f, indent=2)
        
        return synthesized
    
    def _run_mutation_testing(
        self,
        programs: List[Program],
        synthesized_specs: List['ACSLSpec']
    ) -> tuple:
        """Run mutation testing for both synthesized and gold specs."""
        synthesized_results = []
        gold_results = []
        
        for program, synth_spec in zip(programs, synthesized_specs):
            # Generate mutants
            mutants = self.components['mutant_generator'].generate_mutants(program.c_code)
            
            # Test synthesized spec
            synth_result = self.components['mutation_tester'].compute_kill_rate(
                program.program_id,
                mutants,
                synth_spec,
                "synthesized",
                Path('/tmp/mutation_test')
            )
            synthesized_results.append(synth_result)
            
            # Test gold spec
            gold_result = self.components['mutation_tester'].compute_kill_rate(
                program.program_id,
                mutants,
                program.gold_spec,
                "gold",
                Path('/tmp/mutation_test')
            )
            gold_results.append(gold_result)
        
        return synthesized_results, gold_results
    
    def _analyze_results(
        self,
        synthesized_results: List[KillRateResult],
        gold_results: List[KillRateResult]
    ) -> GateDecision:
        """Compare and make gate decision."""
        comparisons = self.components['analyzer'].compare_specs(
            synthesized_results, gold_results
        )
        return self.components['analyzer'].compute_gate_decision(comparisons)
    
    def _generate_outputs(
        self,
        gate_decision: GateDecision,
        synthesized_results: List[KillRateResult],
        gold_results: List[KillRateResult]
    ):
        """Generate figures and validation report."""
        # Generate figures (handled by MutationVisualizer - not detailed here)
        # Generate validation report (handled by ValidationReporter - not detailed here)
        pass
    
    def _create_mutation_operators(self) -> List[MutationOperator]:
        """Create all 12 mutation operators."""
        return [
            ArithmeticMutation(),
            RelationalMutation(),
            BooleanMutation(),
            StatementMutation(),
            BoundaryMutation()
        ]
    
    def _load_config(self, path: str) -> dict:
        """Load YAML configuration."""
        with open(path) as f:
            return yaml.safe_load(f)
    
    def _serialize_spec(self, spec: 'ACSLSpec') -> dict:
        """Convert ACSLSpec to JSON-serializable dict."""
        return {
            'annotated_code': spec.annotated_code,
            'preconditions': spec.preconditions,
            'postconditions': spec.postconditions,
            'loop_invariants': spec.loop_invariants,
            'assertions': spec.assertions
        }
    
    def _deserialize_spec(self, data: dict) -> 'ACSLSpec':
        """Reconstruct ACSLSpec from dict."""
        from h_m1.code.code.src.llm_client import ACSLSpec
        return ACSLSpec(**data)
```

### Pseudo-code (Pipeline Orchestration)

```
ALGORITHM: Mutation Testing Pipeline

INPUT: config (dataset, operators, thresholds)
OUTPUT: GateDecision (PASS/FAIL)

1. Setup:
   a. Initialize h-m1 components (LLM, verifier, feedback)
   b. Initialize h-c2 components (mutant generator, tester, analyzer)

2. Load Dataset:
   programs = load_acsl_by_example(30 programs, stratified=True)

3. Synthesize Specifications:
   FOR each program:
     IF checkpoint exists:
       spec = load_checkpoint(program.id)
     ELSE:
       spec = refinement_loop.synthesize(program.c_code)
       save_checkpoint(program.id, spec)
     synthesized_specs.append(spec)

4. Mutation Testing:
   FOR each (program, synthesized_spec):
     mutants = generate_mutants(program.c_code, all_operators)
     
     # Test synthesized spec
     synth_result = test_all_mutants(mutants, synthesized_spec)
     
     # Test gold spec
     gold_result = test_all_mutants(mutants, program.gold_spec)
     
     results.append((synth_result, gold_result))

5. Analysis:
   comparisons = compare_kill_rates(synthesized_results, gold_results)
   gate = compute_gate_decision(comparisons, threshold=0.70)

6. Output:
   generate_figures(comparisons)
   generate_validation_report(gate)
   
   RETURN gate
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Pipeline orchestration | End-to-end flow with checkpointing |

---

## External Dependencies API (Base Hypothesis)

**CRITICAL:** The following APIs are called from h-m1. Signatures verified from actual code.

### From h-m1/code/code/src/refinement_loop.py (ACTUAL CODE)

```python
class IterativeRefinementLoop:
    def __init__(
        self,
        generator: SpecificationGenerator,
        verifier: FramaCVerifier,
        feedback_extractor: FeedbackExtractor,
        max_iterations: int = 10,
        no_improvement_threshold: int = 3
    ):
        """
        Args:
            generator: LLM client for spec generation
            verifier: Frama-C wrapper
            feedback_extractor: Structured feedback parser
            max_iterations: Maximum refinement attempts
            no_improvement_threshold: Stop after N iterations with no progress
        """
        pass
    
    def synthesize_specification(
        self,
        c_code: str,
        temp_dir: Path
    ) -> RefinementHistory:
        """
        Complete synthesis pipeline with iterative refinement.
        
        Args:
            c_code: Unannotated C program
            temp_dir: Working directory
        
        Returns:
            RefinementHistory with all iterations
        """
        pass
```

### From h-m1/code/code/src/verifier.py (ACTUAL CODE)

```python
class FramaCVerifier:
    def __init__(
        self,
        timeout_per_obligation: int = 10,
        provers: List[str] = None
    ):
        """
        Args:
            timeout_per_obligation: Seconds per proof (default: 10)
            provers: SMT solvers to use
        """
        pass
    
    def verify(self, acsl_spec: ACSLSpec, temp_dir: Path) -> VerificationResult:
        """
        Verify ACSL specification with Frama-C/WP.
        
        Args:
            acsl_spec: ACSL-annotated C code
            temp_dir: Directory for temporary files
        
        Returns:
            VerificationResult with proof obligations
        """
        pass

@dataclass
class VerificationResult:
    """Frama-C/WP verification output."""
    total_obligations: int
    proved_obligations: int
    failed_obligations: int
    proof_discharge_rate: float
    obligations: List[ProofObligation]
    raw_output: str
```

### From h-m1/code/code/src/llm_client.py (ACTUAL CODE)

```python
@dataclass
class ACSLSpec:
    """ACSL-annotated C program."""
    annotated_code: str
    preconditions: List[str]
    postconditions: List[str]
    loop_invariants: List[str]
    assertions: List[str]

class SpecificationGenerator:
    def __init__(self, api_key: str, model: str = "claude-opus-4-5"):
        """Initialize with Anthropic API client."""
        pass
    
    def generate_initial_spec(
        self,
        c_code: str,
        verification_goal: str = "functional correctness"
    ) -> ACSLSpec:
        """
        Generate ACSL specification from unannotated C code.
        
        Args:
            c_code: Unannotated C program
            verification_goal: What to verify
        
        Returns:
            ACSLSpec with annotated code
        """
        pass
```

### From h-m1/code/code/src/feedback_parser.py (ACTUAL CODE)

```python
class FeedbackExtractor:
    def extract_feedback(
        self,
        result: VerificationResult,
        acsl_spec: ACSLSpec
    ) -> Optional[StructuredFeedback]:
        """
        Extract structured feedback from failed verifications.
        
        Args:
            result: WP output
            acsl_spec: Current specification
        
        Returns:
            StructuredFeedback or None if all proved
        """
        pass
```

**Verified from:** `/workspace/TEST_verifai/docs/youra_research/h-m1/code/code/`

**Critical Notes:**
- Parameter names match actual implementation (no spec divergence)
- h-c2 reuses h-m1's refinement mechanism for specification synthesis
- h-c2 adds mutation testing layer on top of h-m1's synthesis

---

## Summary

This logic document provides copy-paste ready APIs for Phase 4 implementation.

**Delivered Components:**
1. MutationOperator + 5 subclasses: AST-based C code mutation
2. MutantGenerator: Parse, mutate, filter compilable
3. MutationTester: Verify mutants, compute kill rates
4. SpecificationSynthesizer: Wrap h-m1 refinement loop
5. DatasetLoader: ACSL-by-Example loading
6. ComparisonAnalyzer: Kill rate comparison + gate decision
7. MutationExperimentRunner: End-to-end pipeline orchestration

**Critical Verification:**
- Base h-m1 APIs verified from actual code (no spec-code divergence)
- All parameter names match implementation
- Integration pattern reuses h-m1 synthesis, adds mutation validation layer

**Ready for Phase 4:** All signatures include type hints and are copy-paste ready.

**Total Budget:** 11 subtasks (2+2+2+1+1+2+1) ✓
