# Core Logic Document: H-E1 Verifier-Feedback-Driven Specification Synthesis

**Date:** 2026-07-11  
**Hypothesis:** LLMs can utilize structured verifier feedback to iteratively refine formal specifications  
**Phase:** Phase 3 - Logic Design  
**Complexity:** HIGH (Novel iterative refinement mechanism)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New API design - no existing codebase to verify  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## Knowledge Base Research (Archon)

**Applied**: Iterative refinement loop pattern (from LLM research)

**Key Insight**: No formal verification patterns in KB. Implementation based on:
- AutoSpec+ architecture (ACL 2026) - official reference implementation
- Frama-C/WP API documentation
- Standard LLM API integration patterns

---

## Task Allocation Reference

From `03_tasks.yaml`:
- **A-1**: Initial Spec Generation (Complexity: 8, Budget: 10)
- **A-2**: Verification Execution (Complexity: 7, Budget: 8)
- **A-3**: Feedback Extraction (Complexity: 9, Budget: 12) - CRITICAL
- **A-4**: Iterative Refinement Loop (Complexity: 8, Budget: 10)
- **A-5**: Metrics Tracking (Complexity: 5, Budget: 6)

Total Budget: 46 subtasks

---

## A-1: Initial Specification Generation [Complexity: 8, Budget: 10]

**Applied**: Standard LLM prompt engineering with structured output

### API Signatures

```python
from typing import Optional, List, Dict
from dataclasses import dataclass
from anthropic import Anthropic

@dataclass
class ACSLSpec:
    """ACSL-annotated C program."""
    annotated_code: str  # Full C code with ACSL comments
    preconditions: List[str]  # Extracted preconditions
    postconditions: List[str]  # Extracted postconditions
    loop_invariants: List[str]  # Extracted loop invariants
    assertions: List[str]  # Extracted assertions

class SpecificationGenerator:
    """Generate initial ACSL specifications from C code."""
    
    def __init__(self, api_key: str, model: str = "claude-opus-4-5"):
        """Initialize with Anthropic API client."""
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.few_shot_examples = self._load_few_shot_examples()
    
    def generate_initial_spec(
        self, 
        c_code: str, 
        verification_goal: str = "functional correctness"
    ) -> ACSLSpec:
        """
        Generate ACSL specification from unannotated C code.
        
        c_code: str - Unannotated C program
        verification_goal: str - What to verify (default: functional correctness)
        
        Returns: ACSLSpec with annotated code and extracted clauses
        """
        prompt = self._construct_generation_prompt(c_code, verification_goal)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.7,  # Higher for initial generation
            messages=[{"role": "user", "content": prompt}]
        )
        
        annotated_code = self._extract_code_from_response(response.content)
        return self._parse_acsl_spec(annotated_code)
    
    def _construct_generation_prompt(self, c_code: str, goal: str) -> str:
        """Build prompt with ACSL grammar + few-shot examples."""
        return f"""Generate ACSL formal specification for this C program.

VERIFICATION GOAL: {goal}

ACSL GRAMMAR (Essential Constructs):
- Function contracts: /*@ requires P; ensures Q; */
- Loop invariants: /*@ loop invariant I; */
- Assertions: /*@ assert P; */
- Logic functions: /*@ logic type name(args) = expr; */

FEW-SHOT EXAMPLES:
{self.few_shot_examples}

C PROGRAM TO ANNOTATE:
```c
{c_code}
```

REQUIREMENTS:
1. Add preconditions (requires) for all function parameters
2. Add postconditions (ensures) for return values and side effects
3. Add loop invariants for all loops
4. Use ACSL \\result for return value in postconditions
5. Use \\valid(ptr) for pointer validity
6. Use \\old(x) for pre-state values in postconditions

OUTPUT FORMAT:
Return ONLY the C code with ACSL annotations as comments.
"""
    
    def _load_few_shot_examples(self) -> str:
        """Load 3-5 examples from ACSL-by-Example."""
        # Example: binary search with verified ACSL
        return """
EXAMPLE 1: Binary Search
```c
/*@ requires n >= 0;
  @ requires \\valid_read(arr + (0..n-1));
  @ requires \\forall integer i, j; 0 <= i < j < n ==> arr[i] <= arr[j];
  @ ensures (\\result >= 0 && \\result < n) ==> arr[\\result] == value;
  @ ensures (\\result == -1) ==> \\forall integer i; 0 <= i < n ==> arr[i] != value;
  @*/
int binary_search(int *arr, int n, int value) {
    int low = 0, high = n - 1;
    /*@ loop invariant 0 <= low && high < n;
      @ loop invariant \\forall integer i; 0 <= i < low || high < i < n ==> arr[i] != value;
      @ loop variant high - low;
      @*/
    while (low <= high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] == value) return mid;
        if (arr[mid] < value) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}
```

EXAMPLE 2: Maximum Element
```c
/*@ requires n > 0;
  @ requires \\valid_read(arr + (0..n-1));
  @ ensures \\result >= 0 && \\result < n;
  @ ensures \\forall integer i; 0 <= i < n ==> arr[i] <= arr[\\result];
  @*/
int find_max(int *arr, int n) {
    int max_idx = 0;
    /*@ loop invariant 1 <= i <= n;
      @ loop invariant 0 <= max_idx < i;
      @ loop invariant \\forall integer j; 0 <= j < i ==> arr[j] <= arr[max_idx];
      @ loop variant n - i;
      @*/
    for (int i = 1; i < n; i++) {
        if (arr[i] > arr[max_idx]) max_idx = i;
    }
    return max_idx;
}
```
"""
    
    def _extract_code_from_response(self, content: List) -> str:
        """Extract C code from LLM response (handles markdown blocks)."""
        text = content[0].text
        # Extract code between ```c and ```
        if "```c" in text:
            start = text.find("```c") + 4
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()
    
    def _parse_acsl_spec(self, annotated_code: str) -> ACSLSpec:
        """Parse ACSL clauses from annotated code."""
        import re
        
        # Extract all ACSL comments
        acsl_pattern = r'/\*@(.*?)\*/'
        clauses = re.findall(acsl_pattern, annotated_code, re.DOTALL)
        
        preconditions = []
        postconditions = []
        loop_invariants = []
        assertions = []
        
        for clause in clauses:
            if 'requires' in clause:
                preconditions.extend(re.findall(r'requires\s+(.*?);', clause))
            if 'ensures' in clause:
                postconditions.extend(re.findall(r'ensures\s+(.*?);', clause))
            if 'loop invariant' in clause:
                loop_invariants.extend(re.findall(r'loop invariant\s+(.*?);', clause))
            if 'assert' in clause:
                assertions.extend(re.findall(r'assert\s+(.*?);', clause))
        
        return ACSLSpec(
            annotated_code=annotated_code,
            preconditions=preconditions,
            postconditions=postconditions,
            loop_invariants=loop_invariants,
            assertions=assertions
        )
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | API client init | Initialize Anthropic SDK |
| L-1-2 | Few-shot loader | Load ACSL examples from dataset |
| L-1-3 | ACSL grammar template | Define ACSL syntax reference |
| L-1-4 | Prompt constructor | Build generation prompt |
| L-1-5 | LLM invocation | Call API with retry logic |
| L-1-6 | Response parser | Extract code from markdown |
| L-1-7 | ACSL clause extractor | Regex-based clause parsing |
| L-1-8 | Validation | Check ACSL syntax validity |
| L-1-9 | Error handling | Retry on malformed output |
| L-1-10 | Token tracking | Log API usage |

---

## A-2: Verification Execution [Complexity: 7, Budget: 8]

**Applied**: Standard subprocess pattern for external tool integration

### API Signatures

```python
import subprocess
from pathlib import Path
from enum import Enum

class ProofStatus(Enum):
    """Proof obligation status from Frama-C/WP."""
    VALID = "Valid"  # Proved by SMT solver
    QED = "Qed"  # Trivially proved
    UNKNOWN = "Unknown"  # Solver timeout/failure
    INVALID = "Invalid"  # Counterexample found

@dataclass
class ProofObligation:
    """Single verification condition."""
    obligation_id: str  # e.g., "loop_inv_preserved_1"
    location: str  # File:Line:Function
    obligation_type: str  # precondition | postcondition | loop_invariant | assertion
    formula: str  # ACSL formula being verified
    status: ProofStatus
    prover: Optional[str]  # alt-ergo | z3
    time_ms: float

@dataclass
class VerificationResult:
    """Frama-C/WP verification output."""
    total_obligations: int
    proved_obligations: int
    failed_obligations: int
    proof_discharge_rate: float  # (proved / total) * 100
    obligations: List[ProofObligation]
    raw_output: str  # Full WP output for debugging

class FramaCVerifier:
    """Execute Frama-C/WP and parse results."""
    
    def __init__(
        self, 
        timeout_per_obligation: int = 10,
        provers: List[str] = ["alt-ergo", "z3"]
    ):
        """
        timeout_per_obligation: int - Seconds per proof (default: 10)
        provers: List[str] - SMT solvers to use
        """
        self.timeout = timeout_per_obligation
        self.provers = provers
        self._check_installation()
    
    def verify(self, acsl_spec: ACSLSpec, temp_dir: Path) -> VerificationResult:
        """
        Verify ACSL specification with Frama-C/WP.
        
        acsl_spec: ACSLSpec - Annotated C code
        temp_dir: Path - Directory for temporary files
        
        Returns: VerificationResult with proof obligations
        """
        # Write annotated code to file
        c_file = temp_dir / "program.c"
        c_file.write_text(acsl_spec.annotated_code)
        
        # Execute Frama-C/WP
        cmd = [
            "frama-c",
            "-wp",
            f"-wp-timeout {self.timeout}",
            f"-wp-prover {','.join(self.provers)}",
            "-wp-out", str(temp_dir),
            "-wp-report", str(temp_dir / "report.json"),
            str(c_file)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout * 100  # Overall timeout
            )
            
            # Parse WP output
            return self._parse_wp_output(result.stdout, temp_dir)
        
        except subprocess.TimeoutExpired:
            return VerificationResult(
                total_obligations=0,
                proved_obligations=0,
                failed_obligations=0,
                proof_discharge_rate=0.0,
                obligations=[],
                raw_output="TIMEOUT"
            )
    
    def _parse_wp_output(self, stdout: str, temp_dir: Path) -> VerificationResult:
        """Parse Frama-C/WP text output and JSON report."""
        import json
        
        # Parse JSON report (contains structured data)
        report_file = temp_dir / "report.json"
        if report_file.exists():
            with open(report_file) as f:
                report = json.load(f)
            return self._parse_json_report(report, stdout)
        
        # Fallback: parse text output
        return self._parse_text_output(stdout)
    
    def _parse_json_report(self, report: Dict, raw_output: str) -> VerificationResult:
        """Parse structured JSON report from WP."""
        obligations = []
        
        for goal in report.get("goals", []):
            obligations.append(ProofObligation(
                obligation_id=goal["id"],
                location=f"{goal['file']}:{goal['line']}:{goal['function']}",
                obligation_type=goal["kind"],
                formula=goal["property"],
                status=ProofStatus(goal["status"]),
                prover=goal.get("prover"),
                time_ms=goal.get("time", 0.0)
            ))
        
        proved = sum(1 for o in obligations if o.status in [ProofStatus.VALID, ProofStatus.QED])
        total = len(obligations)
        
        return VerificationResult(
            total_obligations=total,
            proved_obligations=proved,
            failed_obligations=total - proved,
            proof_discharge_rate=(proved / total * 100) if total > 0 else 0.0,
            obligations=obligations,
            raw_output=raw_output
        )
    
    def _parse_text_output(self, stdout: str) -> VerificationResult:
        """Fallback text parser (when JSON not available)."""
        import re
        
        # Parse text patterns like:
        # [wp] [Alt-Ergo] goal typed_binary_search_post: Valid (Cached)
        pattern = r'\[wp\].*?goal\s+(\S+):\s+(Valid|Qed|Unknown|Invalid)'
        matches = re.findall(pattern, stdout)
        
        obligations = [
            ProofObligation(
                obligation_id=match[0],
                location="unknown",
                obligation_type="unknown",
                formula="",
                status=ProofStatus(match[1]),
                prover=None,
                time_ms=0.0
            )
            for match in matches
        ]
        
        proved = sum(1 for o in obligations if o.status in [ProofStatus.VALID, ProofStatus.QED])
        total = len(obligations)
        
        return VerificationResult(
            total_obligations=total,
            proved_obligations=proved,
            failed_obligations=total - proved,
            proof_discharge_rate=(proved / total * 100) if total > 0 else 0.0,
            obligations=obligations,
            raw_output=stdout
        )
    
    def _check_installation(self):
        """Verify Frama-C/WP is installed."""
        try:
            subprocess.run(["frama-c", "-version"], capture_output=True, check=True)
        except FileNotFoundError:
            raise RuntimeError("Frama-C not installed. Run: opam install frama-c")
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Command builder | Construct frama-c CLI args |
| L-2-2 | Subprocess execution | Run verifier with timeout |
| L-2-3 | JSON report parser | Parse structured WP output |
| L-2-4 | Text parser fallback | Regex-based parsing |
| L-2-5 | Status enum mapping | Map WP statuses to enum |
| L-2-6 | Proof obligation extraction | Build obligation objects |
| L-2-7 | Metrics computation | Calculate discharge rate |
| L-2-8 | Error handling | Timeout and crash recovery |

---

## A-3: Feedback Extraction (3 Dimensions) [Complexity: 9, Budget: 12]

**Applied**: Custom pattern for formal verification feedback parsing

**CRITICAL COMPONENT**: This implements the 3-dimensional feedback structure from hypothesis.

### API Signatures

```python
from typing import Set, Tuple

@dataclass
class WitnessInstantiation:
    """Dimension 1: Concrete counterexample values."""
    failed_obligation_id: str
    witness_values: Dict[str, str]  # Variable -> concrete value
    violating_path: List[str]  # Execution path leading to violation

@dataclass
class LogicalStructure:
    """Dimension 2: Which proof obligation failed."""
    failed_obligations: List[ProofObligation]
    failure_summary: str  # Human-readable description
    critical_failures: List[str]  # Blocking failures (preconditions, etc.)

@dataclass
class DependencyPreservation:
    """Dimension 3: Inter-specification dependencies."""
    broken_dependencies: List[Tuple[str, str]]  # (clause_id, depends_on_id)
    dependency_chain: List[str]  # Ordered dependency violations
    suggested_fixes: List[str]  # Heuristic fix suggestions

@dataclass
class StructuredFeedback:
    """Complete 3-dimensional feedback."""
    witness: WitnessInstantiation
    structure: LogicalStructure
    dependency: DependencyPreservation
    natural_language: str  # LLM-consumable description

class FeedbackExtractor:
    """Extract 3-dimensional feedback from verification results."""
    
    def extract_feedback(
        self, 
        result: VerificationResult,
        acsl_spec: ACSLSpec
    ) -> StructuredFeedback:
        """
        Extract structured feedback from failed verifications.
        
        result: VerificationResult - WP output
        acsl_spec: ACSLSpec - Current specification
        
        Returns: StructuredFeedback with all 3 dimensions
        """
        failed = [o for o in result.obligations if o.status not in [ProofStatus.VALID, ProofStatus.QED]]
        
        if not failed:
            return None  # All proved - no feedback needed
        
        # Dimension 1: Witness Instantiation
        witness = self._extract_witness(failed, result.raw_output)
        
        # Dimension 2: Logical Structure
        structure = self._analyze_logical_structure(failed, acsl_spec)
        
        # Dimension 3: Dependency Preservation
        dependency = self._analyze_dependencies(failed, acsl_spec)
        
        # Convert to natural language for LLM
        nl_feedback = self._format_for_llm(witness, structure, dependency)
        
        return StructuredFeedback(
            witness=witness,
            structure=structure,
            dependency=dependency,
            natural_language=nl_feedback
        )
    
    def _extract_witness(
        self, 
        failed: List[ProofObligation],
        raw_output: str
    ) -> WitnessInstantiation:
        """
        Dimension 1: Parse counterexample values from WP output.
        
        Frama-C/WP output format (when counterexample available):
        [wp] [Alt-Ergo] goal loop_inv: Invalid
        Counter-example:
          x = 5
          y = -1
          arr[0] = 10
        """
        import re
        
        # Most critical failure (first failed precondition or loop invariant)
        critical = failed[0]
        
        # Parse counterexample section
        witness_pattern = r'Counter-example:\s+((?:\s+\w+(?:\[\d+\])?\s*=\s*[^\n]+\n?)+)'
        match = re.search(witness_pattern, raw_output)
        
        witness_values = {}
        violating_path = []
        
        if match:
            witness_text = match.group(1)
            # Parse variable assignments: x = 5
            assignments = re.findall(r'(\w+(?:\[\d+\])?)\s*=\s*([^\n]+)', witness_text)
            witness_values = {var: val.strip() for var, val in assignments}
            
            # Extract execution path (if available in output)
            path_pattern = r'Execution path:.*?->\s*(\w+)'
            violating_path = re.findall(path_pattern, raw_output)
        
        return WitnessInstantiation(
            failed_obligation_id=critical.obligation_id,
            witness_values=witness_values,
            violating_path=violating_path or ["unknown"]
        )
    
    def _analyze_logical_structure(
        self, 
        failed: List[ProofObligation],
        acsl_spec: ACSLSpec
    ) -> LogicalStructure:
        """
        Dimension 2: Identify which types of obligations failed.
        
        Priority: precondition > postcondition > loop_invariant > assertion
        Rationale: Precondition failures block everything downstream
        """
        # Group failures by type
        by_type = {
            "precondition": [],
            "postcondition": [],
            "loop_invariant": [],
            "assertion": []
        }
        
        for obligation in failed:
            otype = obligation.obligation_type
            if otype in by_type:
                by_type[otype].append(obligation)
        
        # Identify critical failures
        critical = []
        if by_type["precondition"]:
            critical.extend([o.obligation_id for o in by_type["precondition"]])
        if by_type["loop_invariant"]:
            critical.extend([o.obligation_id for o in by_type["loop_invariant"]])
        
        # Generate summary
        summary_parts = []
        for otype, obligations in by_type.items():
            if obligations:
                summary_parts.append(f"{len(obligations)} {otype}(s) failed")
        
        summary = "Verification failures: " + ", ".join(summary_parts)
        
        return LogicalStructure(
            failed_obligations=failed,
            failure_summary=summary,
            critical_failures=critical
        )
    
    def _analyze_dependencies(
        self, 
        failed: List[ProofObligation],
        acsl_spec: ACSLSpec
    ) -> DependencyPreservation:
        """
        Dimension 3: Detect inter-specification dependencies.
        
        Heuristic rules:
        - Loop invariant depends on precondition assumptions
        - Postcondition depends on loop invariant preservation
        - Assertions depend on prior statements
        """
        broken_deps = []
        dependency_chain = []
        suggested_fixes = []
        
        # Rule 1: If precondition failed, all downstream obligations affected
        precond_failed = any(o.obligation_type == "precondition" for o in failed)
        if precond_failed:
            dependency_chain.append("precondition_violation")
            suggested_fixes.append("Strengthen function preconditions to exclude invalid inputs")
        
        # Rule 2: If loop invariant failed, check if it depends on precondition
        loop_inv_failed = [o for o in failed if o.obligation_type == "loop_invariant"]
        if loop_inv_failed and acsl_spec.preconditions:
            for inv in loop_inv_failed:
                # Check if invariant uses variables constrained by precondition
                for precond in acsl_spec.preconditions:
                    if self._shares_variables(inv.formula, precond):
                        broken_deps.append((inv.obligation_id, "precondition"))
                        dependency_chain.append(f"{inv.obligation_id}_depends_on_precondition")
                        suggested_fixes.append(f"Loop invariant {inv.obligation_id} must preserve precondition assumptions")
        
        # Rule 3: If postcondition failed, check loop invariant relationship
        postcond_failed = [o for o in failed if o.obligation_type == "postcondition"]
        if postcond_failed and acsl_spec.loop_invariants:
            for post in postcond_failed:
                for inv in acsl_spec.loop_invariants:
                    if self._shares_variables(post.formula, inv):
                        broken_deps.append((post.obligation_id, "loop_invariant"))
                        dependency_chain.append(f"{post.obligation_id}_depends_on_loop_invariant")
                        suggested_fixes.append(f"Strengthen loop invariant to imply postcondition: {inv}")
        
        return DependencyPreservation(
            broken_dependencies=broken_deps,
            dependency_chain=dependency_chain,
            suggested_fixes=suggested_fixes
        )
    
    def _shares_variables(self, formula1: str, formula2: str) -> bool:
        """Check if two ACSL formulas share common variables."""
        import re
        
        # Extract variable names (simplified heuristic)
        var_pattern = r'\b[a-z_][a-z0-9_]*\b'
        vars1 = set(re.findall(var_pattern, formula1.lower()))
        vars2 = set(re.findall(var_pattern, formula2.lower()))
        
        # Filter out ACSL keywords
        keywords = {"requires", "ensures", "loop", "invariant", "assert", "result", "old", "valid"}
        vars1 -= keywords
        vars2 -= keywords
        
        return bool(vars1 & vars2)
    
    def _format_for_llm(
        self,
        witness: WitnessInstantiation,
        structure: LogicalStructure,
        dependency: DependencyPreservation
    ) -> str:
        """Convert structured feedback to natural language prompt."""
        
        feedback_parts = [
            "VERIFICATION FEEDBACK:",
            "",
            f"SUMMARY: {structure.failure_summary}",
            ""
        ]
        
        # Dimension 1: Witness
        if witness.witness_values:
            feedback_parts.append("COUNTEREXAMPLE (Dimension 1: Witness Instantiation):")
            feedback_parts.append(f"Failed obligation: {witness.failed_obligation_id}")
            feedback_parts.append("Concrete values that violate specification:")
            for var, val in witness.witness_values.items():
                feedback_parts.append(f"  - {var} = {val}")
            if witness.violating_path:
                feedback_parts.append(f"Execution path: {' -> '.join(witness.violating_path)}")
            feedback_parts.append("")
        
        # Dimension 2: Logical Structure
        feedback_parts.append("FAILED OBLIGATIONS (Dimension 2: Logical Structure):")
        for obligation in structure.failed_obligations[:5]:  # Limit to 5 most relevant
            feedback_parts.append(f"  - {obligation.obligation_type} at {obligation.location}")
            feedback_parts.append(f"    Formula: {obligation.formula}")
            feedback_parts.append(f"    Status: {obligation.status.value}")
        feedback_parts.append("")
        
        # Dimension 3: Dependencies
        if dependency.broken_dependencies:
            feedback_parts.append("DEPENDENCY VIOLATIONS (Dimension 3: Preservation):")
            for clause_id, depends_on in dependency.broken_dependencies:
                feedback_parts.append(f"  - {clause_id} depends on {depends_on} (broken)")
            feedback_parts.append("")
        
        # Suggested fixes
        if dependency.suggested_fixes:
            feedback_parts.append("SUGGESTED REFINEMENTS:")
            for fix in dependency.suggested_fixes:
                feedback_parts.append(f"  - {fix}")
            feedback_parts.append("")
        
        return "\n".join(feedback_parts)
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Counterexample parser | Regex extract witness values |
| L-3-2 | Execution path extraction | Parse violating path |
| L-3-3 | Obligation type classifier | Group by precond/postcond/inv |
| L-3-4 | Critical failure detection | Identify blocking failures |
| L-3-5 | Failure summary generator | Human-readable summary |
| L-3-6 | Dependency graph builder | Detect clause dependencies |
| L-3-7 | Variable overlap checker | Find shared variables |
| L-3-8 | Precondition propagation | Track precond impact |
| L-3-9 | Loop invariant analysis | Check inv preservation |
| L-3-10 | Fix suggestion heuristics | Generate refinement hints |
| L-3-11 | NL formatter | Convert to LLM prompt |
| L-3-12 | Feedback validation | Check completeness |

---

## A-4: Iterative Refinement Loop [Complexity: 8, Budget: 10]

**Applied**: Standard iterative refinement with convergence detection

### API Signatures

```python
from enum import Enum

class ConvergenceReason(Enum):
    """Why the loop terminated."""
    ALL_PROVED = "all_proved"  # Success: 100% discharge
    MAX_ITERATIONS = "max_iterations"  # Limit reached
    NO_IMPROVEMENT = "no_improvement"  # Stuck (3 iterations no progress)
    ERROR = "error"  # LLM or verifier error

@dataclass
class RefinementIteration:
    """Single iteration state."""
    iteration: int
    spec: ACSLSpec
    result: VerificationResult
    feedback: Optional[StructuredFeedback]
    proof_discharge_rate: float

@dataclass
class RefinementHistory:
    """Complete refinement process."""
    iterations: List[RefinementIteration]
    final_spec: ACSLSpec
    convergence_reason: ConvergenceReason
    total_iterations: int
    improvement_achieved: bool  # Did ANY iteration improve?

class IterativeRefinementLoop:
    """Main refinement orchestrator."""
    
    def __init__(
        self,
        generator: SpecificationGenerator,
        verifier: FramaCVerifier,
        feedback_extractor: FeedbackExtractor,
        max_iterations: int = 10,
        no_improvement_threshold: int = 3
    ):
        """
        max_iterations: int - Maximum refinement attempts
        no_improvement_threshold: int - Stop after N iterations with no progress
        """
        self.generator = generator
        self.verifier = verifier
        self.feedback_extractor = feedback_extractor
        self.max_iterations = max_iterations
        self.no_improvement_threshold = no_improvement_threshold
    
    def synthesize_specification(
        self, 
        c_code: str,
        temp_dir: Path
    ) -> RefinementHistory:
        """
        Complete synthesis pipeline with iterative refinement.
        
        c_code: str - Unannotated C program
        temp_dir: Path - Working directory
        
        Returns: RefinementHistory with all iterations
        """
        # Initial generation
        initial_spec = self.generator.generate_initial_spec(c_code)
        
        iterations = []
        no_improvement_count = 0
        prev_discharge_rate = 0.0
        
        current_spec = initial_spec
        
        for iteration in range(self.max_iterations):
            # Verify current specification
            result = self.verifier.verify(current_spec, temp_dir)
            
            # Record iteration
            iterations.append(RefinementIteration(
                iteration=iteration,
                spec=current_spec,
                result=result,
                feedback=None,  # Will be set below
                proof_discharge_rate=result.proof_discharge_rate
            ))
            
            # Check convergence: All proved
            if result.proof_discharge_rate >= 100.0:
                return RefinementHistory(
                    iterations=iterations,
                    final_spec=current_spec,
                    convergence_reason=ConvergenceReason.ALL_PROVED,
                    total_iterations=iteration + 1,
                    improvement_achieved=self._check_improvement(iterations)
                )
            
            # Extract feedback (3 dimensions)
            feedback = self.feedback_extractor.extract_feedback(result, current_spec)
            iterations[-1].feedback = feedback
            
            # Check improvement
            if result.proof_discharge_rate <= prev_discharge_rate:
                no_improvement_count += 1
            else:
                no_improvement_count = 0  # Reset counter
            
            # Early stopping: No improvement
            if no_improvement_count >= self.no_improvement_threshold:
                return RefinementHistory(
                    iterations=iterations,
                    final_spec=current_spec,
                    convergence_reason=ConvergenceReason.NO_IMPROVEMENT,
                    total_iterations=iteration + 1,
                    improvement_achieved=self._check_improvement(iterations)
                )
            
            # Refine specification using feedback
            current_spec = self._refine_spec(current_spec, feedback, iteration)
            prev_discharge_rate = result.proof_discharge_rate
        
        # Max iterations reached
        return RefinementHistory(
            iterations=iterations,
            final_spec=current_spec,
            convergence_reason=ConvergenceReason.MAX_ITERATIONS,
            total_iterations=self.max_iterations,
            improvement_achieved=self._check_improvement(iterations)
        )
    
    def _refine_spec(
        self,
        current_spec: ACSLSpec,
        feedback: StructuredFeedback,
        iteration: int
    ) -> ACSLSpec:
        """Refinement using LLM with structured feedback."""
        
        prompt = f"""TASK: Refine ACSL specification based on verification feedback.

ITERATION: {iteration + 1}

CURRENT SPECIFICATION:
```c
{current_spec.annotated_code}
```

{feedback.natural_language}

REFINEMENT INSTRUCTIONS:
1. Analyze the counterexample values (Dimension 1: Witness)
2. Identify which proof obligations failed (Dimension 2: Structure)
3. Fix dependency violations (Dimension 3: Dependencies)
4. Preserve already-proved obligations (do NOT weaken working specs)
5. Focus on critical failures first (preconditions, loop invariants)

REFINEMENT STRATEGIES:
- If precondition failed: Strengthen requires clauses to exclude counterexample
- If loop invariant failed: Adjust invariant to hold at loop entry/preservation/exit
- If postcondition failed: Check if loop invariant implies postcondition
- If dependency broken: Ensure dependent clauses are consistent

OUTPUT FORMAT:
Return ONLY the refined C code with updated ACSL annotations.
"""
        
        response = self.generator.client.messages.create(
            model=self.generator.model,
            max_tokens=4096,
            temperature=0.5,  # Lower temperature for refinement (more conservative)
            messages=[{"role": "user", "content": prompt}]
        )
        
        refined_code = self.generator._extract_code_from_response(response.content)
        return self.generator._parse_acsl_spec(refined_code)
    
    def _check_improvement(self, iterations: List[RefinementIteration]) -> bool:
        """Check if ANY iteration improved proof discharge rate."""
        if len(iterations) < 2:
            return False
        
        for i in range(1, len(iterations)):
            if iterations[i].proof_discharge_rate > iterations[i-1].proof_discharge_rate:
                return True
        
        return False
```

### Pseudo-code (Algorithm Flow)

```
ALGORITHM: Verifier-Feedback-Driven Iterative Refinement

INPUT: c_code (unannotated C program)
OUTPUT: (acsl_spec, convergence_reason, iterations)

1. spec = LLM.generate_initial(c_code)  # Temperature: 0.7
2. iteration = 0
3. prev_rate = 0.0
4. no_improvement_count = 0

5. WHILE iteration < MAX_ITERATIONS:
6.     result = FramaC.verify(spec)
7.     
8.     IF result.discharge_rate == 100.0:
9.         RETURN (spec, ALL_PROVED, iteration)
10.    
11.    feedback = extract_3d_feedback(result, spec)
12.    # Dimension 1: witness.counterexample_values
13.    # Dimension 2: structure.failed_obligations
14.    # Dimension 3: dependency.broken_dependencies
15.    
16.    IF result.discharge_rate <= prev_rate:
17.        no_improvement_count += 1
18.    ELSE:
19.        no_improvement_count = 0
20.    
21.    IF no_improvement_count >= 3:
22.        RETURN (spec, NO_IMPROVEMENT, iteration)
23.    
24.    spec = LLM.refine(spec, feedback)  # Temperature: 0.5
25.    prev_rate = result.discharge_rate
26.    iteration += 1
27.
28. RETURN (spec, MAX_ITERATIONS, iteration)
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Iteration state tracker | Record each iteration |
| L-4-2 | Convergence checker | Detect termination conditions |
| L-4-3 | Improvement detector | Track discharge rate changes |
| L-4-4 | Refinement prompt builder | Construct feedback prompt |
| L-4-5 | LLM refinement call | Invoke API with lower temp |
| L-4-6 | Spec preservation logic | Avoid breaking working parts |
| L-4-7 | Early stopping logic | No-improvement threshold |
| L-4-8 | History aggregator | Build RefinementHistory |
| L-4-9 | Error recovery | Handle LLM/verifier failures |
| L-4-10 | Checkpoint saving | Save intermediate specs |

---

## A-5: Metrics Tracking [Complexity: 5, Budget: 6]

**Applied**: Standard metric computation and logging

### API Signatures

```python
from datetime import datetime
import json

@dataclass
class ExperimentMetrics:
    """Per-program experiment results."""
    program_id: str
    initial_discharge_rate: float
    final_discharge_rate: float
    iterations_to_convergence: int
    convergence_reason: ConvergenceReason
    improvement_achieved: bool
    feedback_dimensions_used: Set[str]  # {"witness", "structure", "dependency"}
    total_api_calls: int
    total_cost_usd: float
    runtime_seconds: float

class MetricsTracker:
    """Track experiment metrics across all programs."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.experiments: List[ExperimentMetrics] = []
    
    def record_experiment(
        self, 
        program_id: str,
        history: RefinementHistory,
        api_calls: int,
        cost_usd: float,
        runtime: float
    ) -> ExperimentMetrics:
        """Record single program experiment."""
        
        # Extract feedback dimensions used
        dimensions_used = set()
        for iteration in history.iterations:
            if iteration.feedback:
                if iteration.feedback.witness.witness_values:
                    dimensions_used.add("witness")
                if iteration.feedback.structure.failed_obligations:
                    dimensions_used.add("structure")
                if iteration.feedback.dependency.broken_dependencies:
                    dimensions_used.add("dependency")
        
        metrics = ExperimentMetrics(
            program_id=program_id,
            initial_discharge_rate=history.iterations[0].proof_discharge_rate if history.iterations else 0.0,
            final_discharge_rate=history.iterations[-1].proof_discharge_rate if history.iterations else 0.0,
            iterations_to_convergence=history.total_iterations,
            convergence_reason=history.convergence_reason,
            improvement_achieved=history.improvement_achieved,
            feedback_dimensions_used=dimensions_used,
            total_api_calls=api_calls,
            total_cost_usd=cost_usd,
            runtime_seconds=runtime
        )
        
        self.experiments.append(metrics)
        
        # Save iteration log
        self._save_iteration_log(program_id, history)
        
        return metrics
    
    def compute_aggregate_metrics(self) -> Dict[str, float]:
        """Compute summary statistics across all experiments."""
        
        if not self.experiments:
            return {}
        
        final_rates = [e.final_discharge_rate for e in self.experiments]
        improvements = [e for e in self.experiments if e.improvement_achieved]
        
        return {
            "mean_final_discharge_rate": sum(final_rates) / len(final_rates),
            "median_final_discharge_rate": sorted(final_rates)[len(final_rates) // 2],
            "min_final_discharge_rate": min(final_rates),
            "max_final_discharge_rate": max(final_rates),
            "programs_with_improvement": len(improvements),
            "improvement_percentage": len(improvements) / len(self.experiments) * 100,
            "mean_iterations": sum(e.iterations_to_convergence for e in self.experiments) / len(self.experiments),
            "total_api_calls": sum(e.total_api_calls for e in self.experiments),
            "total_cost_usd": sum(e.total_cost_usd for e in self.experiments),
            "witness_dimension_usage": sum(1 for e in self.experiments if "witness" in e.feedback_dimensions_used),
            "structure_dimension_usage": sum(1 for e in self.experiments if "structure" in e.feedback_dimensions_used),
            "dependency_dimension_usage": sum(1 for e in self.experiments if "dependency" in e.feedback_dimensions_used)
        }
    
    def save_results(self, filename: str = "04_results.json"):
        """Save all results to JSON."""
        
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "hypothesis": "H-E1",
                "total_programs": len(self.experiments)
            },
            "aggregate_metrics": self.compute_aggregate_metrics(),
            "per_program_metrics": [
                {
                    "program_id": e.program_id,
                    "initial_rate": e.initial_discharge_rate,
                    "final_rate": e.final_discharge_rate,
                    "iterations": e.iterations_to_convergence,
                    "convergence": e.convergence_reason.value,
                    "improved": e.improvement_achieved,
                    "dimensions_used": list(e.feedback_dimensions_used),
                    "cost_usd": e.total_cost_usd
                }
                for e in self.experiments
            ]
        }
        
        output_file = self.output_dir / filename
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
    
    def _save_iteration_log(self, program_id: str, history: RefinementHistory):
        """Save detailed iteration log for debugging."""
        
        log_data = {
            "program_id": program_id,
            "total_iterations": history.total_iterations,
            "convergence_reason": history.convergence_reason.value,
            "iterations": [
                {
                    "iteration": it.iteration,
                    "discharge_rate": it.proof_discharge_rate,
                    "total_obligations": it.result.total_obligations,
                    "proved_obligations": it.result.proved_obligations,
                    "feedback_summary": it.feedback.natural_language if it.feedback else None
                }
                for it in history.iterations
            ]
        }
        
        log_file = self.output_dir / f"{program_id}_iteration_log.json"
        with log_file.open("w") as f:
            json.dump(log_data, f, indent=2)
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Per-iteration metrics | Track discharge rate per iteration |
| L-5-2 | Dimension usage tracker | Record feedback dimension usage |
| L-5-3 | Aggregate statistics | Compute mean/median/std |
| L-5-4 | JSON serialization | Save results to file |
| L-5-5 | Iteration log writer | Save detailed logs |
| L-5-6 | Cost tracking | Track API usage/cost |

---

## Edge Case Handling

### Case 1: Malformed ACSL from LLM

**Problem**: LLM generates syntactically invalid ACSL.

**Detection**: Frama-C parsing error (exit code != 0).

**Recovery**:
```python
def _validate_acsl_syntax(annotated_code: str) -> bool:
    """Pre-validate ACSL before verification."""
    # Run frama-c -parse-only
    result = subprocess.run(
        ["frama-c", "-parse-only", "-"],
        input=annotated_code,
        capture_output=True,
        text=True
    )
    return result.returncode == 0

# In refinement loop:
if not _validate_acsl_syntax(refined_spec.annotated_code):
    # Retry with explicit syntax correction prompt
    prompt = f"Previous output had ACSL syntax errors. Fix syntax: {refined_spec.annotated_code}"
    # Retry up to 3 times, then skip program
```

### Case 2: Verifier Timeout

**Problem**: Frama-C/WP exceeds timeout on complex proofs.

**Detection**: subprocess.TimeoutExpired exception.

**Recovery**:
```python
try:
    result = subprocess.run(cmd, timeout=timeout * 100)
except subprocess.TimeoutExpired:
    # Return partial results (obligations that finished)
    return VerificationResult(
        total_obligations=0,
        proved_obligations=0,
        failed_obligations=0,
        proof_discharge_rate=0.0,
        obligations=[],
        raw_output="TIMEOUT"
    )
```

### Case 3: LLM Hallucination (Random Changes)

**Problem**: LLM ignores feedback and makes arbitrary changes.

**Detection**: Manual inspection + no improvement in discharge rate.

**Mitigation**:
```python
# Add chain-of-thought reasoning to refinement prompt:
prompt = f"""Before refining, explain:
1. What does the counterexample tell you?
2. Which obligation is most critical to fix?
3. What specific change will address the failure?

REASONING:
[Your analysis here]

REFINED SPECIFICATION:
[Updated code here]
"""
```

### Case 4: No Counterexample Available

**Problem**: WP output doesn't include counterexample values (solver limitation).

**Detection**: Empty witness_values dict.

**Fallback**:
```python
if not witness.witness_values:
    # Use structural feedback only (Dimensions 2 & 3)
    feedback.natural_language = f"""
    VERIFICATION FEEDBACK (No counterexample available):
    
    {structure.failure_summary}
    
    Failed obligations: {len(structure.failed_obligations)}
    Focus on: {structure.critical_failures}
    
    Suggested fixes:
    {chr(10).join(dependency.suggested_fixes)}
    """
```

---

## Algorithm Complexity Analysis

### Time Complexity (Per Program)

**Component Costs**:
1. **Initial Generation**: 1 LLM call (~10-30s)
2. **Verification**: 1 Frama-C call per iteration (~5-60s depending on program size)
3. **Feedback Extraction**: O(n) where n = number of obligations (~1s)
4. **Refinement**: 1 LLM call per iteration (~10-30s)

**Total per program**:
```
T = T_init + iterations × (T_verify + T_feedback + T_refine)
  = 20s + 10 × (30s + 1s + 20s)
  = 20s + 10 × 51s
  = 530s (~9 minutes per program)
```

**For 5-10 programs**: 45-90 minutes total runtime

### API Call Budget

**Per program**:
- Initial generation: 1 call
- Refinement: 10 calls (max iterations)
- **Total**: 11 calls per program

**For 10 programs**: 110 API calls

**Cost estimation** (Claude Opus 4.5):
- Input tokens: ~2000/call (prompt + code)
- Output tokens: ~1500/call (annotated code)
- Cost per call: ~$0.03
- **Total cost**: 110 × $0.03 = **$3.30** (within $0.50-5.00 budget)

### Space Complexity

**Memory usage**:
- ACSL spec storage: O(code_size) ~10KB per program
- Verification results: O(obligations) ~1KB per result
- Iteration history: O(iterations × obligations) ~100KB per program

**Total for 10 programs**: ~1MB (negligible)

---

## Summary

This logic document provides **runnable pseudo-code** for the complete verifier-feedback-driven iterative refinement system. Phase 4 Coder can directly implement the provided API signatures.

**Key Components Delivered**:
1. Initial spec generation with few-shot ACSL examples
2. Frama-C/WP integration with JSON/text parsing
3. **3-dimensional feedback extraction** (witness + structure + dependency)
4. Iterative refinement loop with convergence detection
5. Comprehensive metrics tracking

**Critical Algorithmic Contributions**:
- Witness extraction from WP counterexamples
- Dependency heuristics for ACSL clause relationships
- Natural language feedback formatting for LLM consumption
- Convergence detection with early stopping

**Ready for Phase 4**: All signatures are copy-paste ready with type hints and tensor/data structure shapes documented inline.
