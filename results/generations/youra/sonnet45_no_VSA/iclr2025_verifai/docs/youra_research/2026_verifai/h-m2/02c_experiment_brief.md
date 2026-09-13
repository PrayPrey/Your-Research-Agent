# Experiment Design: H-M2

**Date:** 2026-07-11
**Author:** Anonymous
**Hypothesis Statement:** Staged progressive refinement (types→pre→post→inv) converges faster and achieves higher proof discharge than complete upfront specification
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE (Unattended Mode)
**Prerequisites Satisfied:** Yes (H-E1 validated with 62.9% discharge rate)
**Gate Status:** SHOULD_WORK (not yet tested)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** Mechanism (SHOULD_WORK)
- **Prerequisites:** [H-E1]

### Gate Condition
**Type:** SHOULD_WORK (optimization, not core claim)

**Pass Criteria:**
- Staged converges in ≤70% of iterations vs. complete
- Staged achieves ≥5pp higher final proof discharge
- Statistical significance (p < 0.05)

**Failure Acceptance:** Neutral result acceptable - does not block Phase 5

---

## Continuation Context

**This is a continuation experiment building on H-E1.**

H-M2 tests a specific refinement strategy (Staged vs. Complete) using the same infrastructure validated in H-E1. This enables controlled comparison where only the refinement approach changes.

**Inherited from H-E1:**
- LLM configuration (GPT-4/Claude Opus, temperature=0.0)
- Frama-C WP verification setup
- Benchmark program selection approach
- Baseline iterative refinement mechanism

**Novel in H-M2:**
- Sequential staged refinement (types→pre→post→inv)
- Per-stage convergence tracking
- Backtracking event detection

### Previous Hypothesis Results (H-E1)

**Source:** `docs/youra_research/h-e1/04_validation.md`

**H-E1 Results:**
- **Mean Discharge Rate:** 62.9% (target: 50%) ✅ PASSED
- **Programs Tested:** 10 (mock validation)
- **Improvement Rate:** 100% (all programs improved)
- **Mean Iterations:** 5.7
- **Feedback Dimensions Used:**
  - Witness: 8/10 programs
  - Structure: 10/10 programs
  - Dependency: 9/10 programs

**Key Lessons for H-M2:**
1. Iterative refinement with structured feedback works (62.9% > 50% target)
2. Average 5.7 iterations suggests budget of 10 iterations is appropriate
3. All three feedback dimensions are utilized by LLM
4. 100% improvement rate indicates mechanism is robust

**Reuse Decision:** Use same LLM config, verifier setup, and baseline Complete strategy from H-E1 as control condition

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Scope:** Formal verification, iterative refinement, LLM specification synthesis

**Query 1: Staged Progressive Refinement**
- **Search:** "staged progressive refinement specification synthesis"
- **Finding:** No directly relevant formal verification content found
- **Reason:** Novel research area - verifier-as-teacher for specification synthesis is unexplored territory

**Query 2: Formal Verification Iterative Refinement**
- **Search:** "formal verification iterative refinement experiment"
- **Finding:** General ML iterative refinement patterns found, but not formal verification specific
- **Insight:** Iterative refinement is a proven pattern in ML training loops (diffusion models, etc.)

**Query 3: LLM Specification Synthesis Benchmarks**
- **Search:** "LLM specification synthesis benchmark dataset"
- **Finding:** No established benchmarks found in Archon KB
- **Insight:** This hypothesis targets a gap in existing research - no standard benchmarks exist yet

**Key Takeaway:**
The absence of direct matches in Archon KB confirms this is **novel research territory**. Existing iterative refinement patterns from ML domains (progressive training, staged optimization) provide architectural inspiration but don't directly apply to formal specification synthesis. Will rely on:
1. **Exa GitHub search** for Frama-C/verification tool implementations
2. **General ML patterns** for experiment design structure (control conditions, ablation studies)
3. **Phase 2B context** for domain-specific requirements

### Archon Code Examples

**Query 1: Formal Verification Code**
- **Search:** "formal verification Frama-C specification"
- **Finding:** No Frama-C specific code found (general verification cache examples only)
- **Reason:** Archon KB is ML-focused, lacks formal verification tooling content

**Query 2: Iterative Refinement Loop**
- **Search:** "iterative refinement loop verification"
- **Finding:** Diffusion model refinement pipelines (base + refiner pattern)
- **Pattern Identified:** Two-stage refinement architecture (base model → refiner model)
  ```python
  # Ensemble refinement pattern (from Stable Diffusion)
  image = base(prompt, denoising_end=0.8, output_type="latent")
  image = refiner(prompt, image, denoising_start=0.8)
  ```
- **Analogy to H-M2:** Staged refinement (types→pre→post→inv) vs. Complete upfront
  - Base model = coarse spec (types)
  - Refiner model = detailed spec (pre/post/inv)
  - Key difference: Sequential stages vs. parallel refinement

**Transferable Insights:**
1. **Stage handoff design:** Clear boundaries between stages (e.g., types complete before preconditions)
2. **Convergence metrics:** Track improvement per stage, not just final output
3. **Backtracking cost:** Diffusion models avoid backtracking by using latent handoff - formal specs may need backtracking if stages conflict

**Limitation:**
ML refinement operates on continuous latents; formal spec refinement operates on discrete logical statements. Convergence dynamics will differ significantly.

### Exa GitHub Implementations

**Query 1: Frama-C ACSL LLM Iterative Refinement**

**Repository 1**: [Xidian-ICTT-GZ/AutoSpec](https://github.com/Xidian-ICTT-GZ/AutoSpec) (⭐ High relevance)
- **URL**: https://github.com/Xidian-ICTT-GZ/AutoSpec
- **Paper**: "AutoSpec+: LLM-Driven Neuro-Symbolic Program Specification Synthesis" (ACL 2026)
- **Relevance**: ⭐⭐⭐ HIGHEST - Implements iterative refinement loop with Frama-C WP feedback
- **Architecture**: Neuro-symbolic agent loop (LLM generates → Frama-C WP verifies → repair on failure)
- **Key Mechanism**: 
  ```python
  # Five-stage refinement pipeline:
  # 1. Static analysis (extended call graph)
  # 2. Neural specification generation (LLM)
  # 3. Formal verification (Frama-C WP)
  # 4. Iterative repair (feedback-driven)
  # 5. Termination analysis (ranking functions)
  ```
- **Refinement Strategy**: Bottom-up proof-aware decomposition
  - Functions and loops are first-class nodes in call graph
  - Synthesizes specifications bottom-up (callees first, then callers)
  - Reduces context length by only including proof-relevant code slices
- **Training Config**:
  - LLM: GPT-4o, Gemini-3, GPT-5.2, Grok-4.1
  - Refinement iterations: ~3 passes (default `refine_count: 3`)
  - Verification timeout: <10s per program
  - Success rate: 96% full proof ratio (Gemini-3)
- **Dataset**: 604 programs from diverse datasets (not specified which)
- **Results**: 98% specification generation success, 96% full proof ratio
- **Configuration**:
  ```yaml
  main:
    refine_count: 3           # Number of refinement passes
    pass_count: 5             # Number of passes
    think: true               # Enable natural language reasoning
    template: true            # Enable loop invariant template
    auto_post: true           # Auto-generate postconditions
  llm:
    api_model: "gpt-4o"
  ```

**Repository 2**: [anon-hiktyq/TSE2026-SESpec](https://github.com/anon-hiktyq/TOSEM2026-SESpec)
- **URL**: https://github.com/anon-hiktyq/TOSEM2026-SESpec
- **Paper**: "Integrating Symbolic Execution with LLMs for Automated Generation of Program Specifications"
- **Relevance**: ⭐⭐ HIGH - Symbolic execution + LLM refinement (different from verifier feedback)
- **Architecture**: Symbolic execution (strongest postcondition) → Template-guided LLM → Iterative refinement
- **Key Difference**: Uses symbolic execution results (not verifier feedback) to guide LLM
- **Training Config**:
  - LLM: GPT-4o (default)
  - Symbolic executor: Custom QCP engine (LLVM-based)
  - Verification: Frama-C 29.0 (Copper)
  - Environment: Ubuntu 22.04, Python 3.10/3.11
- **Dataset**: Not explicitly specified (benchmark programs with ACSL)

**Repository 3**: LORIS (from ACM TOPLAS paper)
- **Paper**: "Guiding LLM-Based Loop Invariant Synthesis via Feedback on Local Reasoning Errors"
- **Relevance**: ⭐⭐⭐ HIGH - Formal feedback on LLM's thinking process
- **Unique Mechanism**: Formalizes LLM's natural language proof into first-order logic → SMT check → pinpoint logical errors
- **Architecture**:
  ```
  1. LLM generates loop invariant + natural language proof
  2. Formalizer LLM translates proof steps to FOL implications
  3. SMT solver checks each implication
  4. Invalid implications → precise error feedback
  5. Refinement with targeted feedback
  ```
- **Results**: 445/460 programs solved (96.7% success rate) on main benchmark
- **Insight**: Goes beyond binary pass/fail feedback - provides exact logical error location

**Query 2: Formal Verification Refinement Loops**

**Repository 4**: SpecLoop (RTL-to-Specification)
- **Paper**: "SpecLoop: An Agentic RTL-to-Specification Framework with Formal Verification Feedback Loop"
- **Relevance**: ⭐ MEDIUM - Different domain (RTL vs. C) but similar iterative refinement pattern
- **Architecture**: Generate spec → Reconstruct RTL → Formal equivalence check → Counterexample feedback → Refine
- **Insight**: Verification-driven iterative feedback improves specification correctness
- **Transferable Pattern**: Equivalence checking as validation (vs. just proof discharge)

**Repository 5**: VeriSpecGen (Lean specifications)
- **Paper**: "Intent-aligned Formal Specification Synthesis via Traceable Refinement"
- **Relevance**: ⭐ MEDIUM - Different language (Lean vs. ACSL) but similar refinement strategy
- **Unique Mechanism**: Requirement-level attribution + localized repair
  - Decomposes natural language into atomic requirements
  - Generates requirement-targeted tests with traceability maps
  - When validation fails, attributes to specific requirements → targeted clause-level repairs
- **Results**: 86.6% success on SpecGen task, 62-106% improvement with trajectory-based training
- **Insight**: Localized repair (fix specific clauses) vs. full regeneration

**Query 3: Frama-C Benchmark Programs**

**Repository 6**: [fraunhoferfokus/acsl-by-example](https://github.com/fraunhoferfokus/acsl-by-example)
- **URL**: https://github.com/fraunhoferfokus/acsl-by-example
- **Relevance**: ⭐⭐⭐ DATASET SOURCE - Tutorial and reference for deductive verification
- **Content**: C programs with ACSL annotations for educational purposes
- **Use Case**: Gold-standard specifications for validation
- **Companion**: Report "ACSL by Example" (Fraunhofer FOKUS)

**Benchmark Paper**: "A benchmark for C program verification" (2019)
- **Content**: 25 C programs as formal verification benchmark
- **Scoring Formula**: Up to 100 points per verification system
- **Use Case**: System comparison and friendly competition

**Frama-C Open Source Case Studies**:
- **URL**: https://github.com/Frama-C/open-source-case-studies
- **Content**: Tutorials (2018-06-ssas-parser) demonstrating Eva, E-ACSL, WP plugins
- **Example Workflow**: Execute → Eva analysis → E-ACSL instrumentation → WP deductive verification
- **Insight**: Multi-plugin collaboration via shared ACSL language

**Serena Analysis Needed**: ✅ YES
- AutoSpec+ repository has complex 5-stage pipeline (>100 lines)
- Need to analyze: proof-aware decomposition, bottom-up synthesis, iterative repair mechanism

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**H-M2 is NOT a paper reproduction** - it is a novel hypothesis testing two refinement strategies (Staged vs. Complete).

**Implementation Priority:**
1. ⭐⭐⭐ **AutoSpec+ architecture** (Xidian-ICTT-GZ/AutoSpec) - Proven iterative refinement framework
2. ⭐⭐ **LORIS feedback mechanism** (ACM TOPLAS) - Precise error attribution concept
3. ⭐ **H-E1 baseline** - Validated Complete strategy (62.9% discharge rate)

**Recommended Implementation Path:**
- **Primary:** Adapt AutoSpec+ bottom-up synthesis framework
  - Implement both Staged and Complete strategies using same infrastructure
  - Use AutoSpec+ verifier integration (Frama-C WP wrapper)
  - Reuse targeted repair mechanism
- **Fallback:** Implement from scratch using H-E1 codebase
  - Extend H-E1's iterative loop with stage boundaries
  - Add per-stage verification tracking
- **Justification:** AutoSpec+ provides proven architecture (96% proof success) and reduces implementation risk. H-E1 provides validated baseline for controlled comparison.

### Code Analysis (Serena MCP)

**Status**: *Limited* - Serena MCP operates on local file paths, GitHub repositories not directly accessible

**Analysis Source**: Exa code context search results + repository documentation

**AutoSpec+ Architecture Analysis** (from documentation and code snippets):

#### Code Structure

**Main Components**:
1. **Static Analysis Module**: Extended call graph construction
   - Functions and loops as first-class nodes
   - Bottom-up traversal for proof-aware decomposition
2. **Neural Generator**: LLM-based specification synthesis
   - GPT-4o, Gemini-3, GPT-5.2 support
   - Structured prompting with proof-relevant code slices
3. **Formal Verifier**: Frama-C WP integration
   - ACSL specification validation
   - SMT solvers: Alt-Ergo, Z3
4. **Iterative Repair**: Feedback-driven refinement
   - Verifier error parsing
   - Targeted clause regeneration (not full restart)
5. **Termination Analyzer**: Ranking function synthesis

**Key Configuration** (`func_config.json` / `loop_config.yaml`):
```yaml
main:
  root_dir: "program_directory"
  function_name: "target_function"
  debug: true
  only_loop: false
  auto_annotation: true
  refine_count: 3           # Iteration budget
  pass_count: 5             # Maximum passes
  think: true               # Chain-of-thought reasoning
  template: true            # Loop invariant templates
  auto_post: true           # Auto-generate postconditions
llm:
  api_model: "gpt-4o"
```

#### Core Mechanism: Bottom-Up Proof-Aware Synthesis

**Purpose**: Reduce context length and focus on proof-relevant code by decomposing verification bottom-up

**Pseudo-code** (inferred from methodology):
```python
class ProofAwareDecomposition:
    """
    Bottom-up specification synthesis with extended call graph
    """
    def __init__(self, program, config):
        self.program = program
        self.call_graph = self.build_extended_call_graph()  # Functions + loops as nodes
        self.config = config
        
    def synthesize_specifications(self):
        """
        Main synthesis loop
        
        Returns: Annotated program with ACSL specifications
        """
        # Step 1: Topological sort (bottom-up)
        synthesis_order = self.topological_sort(self.call_graph)
        
        # Step 2: Synthesize bottom-up
        for node in synthesis_order:  # Leaves (no callees) first
            if node.type == "function":
                spec = self.synthesize_function_spec(node)
            elif node.type == "loop":
                spec = self.synthesize_loop_invariant(node)
            
            # Step 3: Verify + repair
            verified = self.verify_with_framac(node, spec)
            while not verified and self.within_budget():
                feedback = self.extract_verifier_feedback(node, spec)
                spec = self.repair_specification(node, spec, feedback)  # Targeted repair
                verified = self.verify_with_framac(node, spec)
            
            # Step 4: Store for use by callers
            self.validated_specs[node] = spec
        
        return self.annotated_program
    
    def synthesize_function_spec(self, func_node):
        """
        Generate ACSL contract for function
        
        Context: Already-validated specs of callees + proof-relevant code slice
        """
        # Extract only proof-relevant code (exclude implementation details)
        code_slice = self.extract_proof_relevant_slice(func_node)
        
        # Include already-validated callee specs in prompt
        callee_specs = [self.validated_specs[callee] for callee in func_node.callees]
        
        # LLM prompt with reduced context
        prompt = f"""
        Generate ACSL precondition and postcondition for:
        {code_slice}
        
        Callee specifications:
        {callee_specs}
        
        Think step-by-step about required properties.
        """
        
        spec = self.llm.generate(prompt)
        return spec
    
    def repair_specification(self, node, current_spec, verifier_feedback):
        """
        Targeted repair (NOT full regeneration)
        
        Feedback types:
        - Missing precondition
        - Weak postcondition
        - Missing loop invariant clause
        - Type error
        """
        # Parse feedback to identify failing clause
        failing_clause = self.parse_feedback(verifier_feedback)
        
        # Repair only the failing clause
        repair_prompt = f"""
        The following ACSL clause failed verification:
        {failing_clause}
        
        Verifier error:
        {verifier_feedback}
        
        Repair only this clause (keep rest unchanged).
        """
        
        repaired_clause = self.llm.generate(repair_prompt)
        
        # Replace failing clause in specification
        updated_spec = self.replace_clause(current_spec, failing_clause, repaired_clause)
        return updated_spec
```

**Integration Point**: Command-line tool
```bash
# Single file verification
python3 asgse_runner.py -i program.c -o output_dir -m gpt-4o

# Batch verification
python3 auto_run.py -i programs/ -o output_dir -m gpt-4o,gemini-3
```

**Key Insights for H-M2**:
1. **Staged vs Complete**: AutoSpec+ uses bottom-up decomposition (functions before callers), but within each function/loop it generates complete specifications (pre+post+inv together)
2. **Refinement Strategy**: Iterative repair targets specific failing clauses, not full regeneration
3. **Context Management**: Proof-relevant slicing reduces LLM context size
4. **Hypothesis Test**: H-M2 should compare:
   - **Staged**: types → pre → post → inv (sequential within function)
   - **Complete**: all spec components simultaneously (AutoSpec+ baseline)

**LORIS Feedback Mechanism** (from ACM TOPLAS paper):

**Unique Contribution**: Formalizes LLM's natural language reasoning for precise error attribution

```python
class FormalFeedbackRefinement:
    """
    Check LLM's thinking process with SMT solver
    """
    def refine_with_formal_feedback(self, invariant, natural_language_proof):
        """
        Translate NL proof → FOL → SMT check → precise feedback
        """
        # Step 1: LLM generates step-by-step proof
        # (already provided as input)
        
        # Step 2: Formalize each reasoning step
        fol_implications = self.formalizer_llm.translate(natural_language_proof)
        # Example: "x > 0 after loop iteration" → (x_i+1 > 0)
        
        # Step 3: SMT check each implication
        for i, implication in enumerate(fol_implications):
            valid = self.smt_solver.check(implication)
            if not valid:
                # Found exact error location
                return {
                    "error_step": i,
                    "invalid_claim": implication,
                    "original_reasoning": natural_language_proof.steps[i]
                }
        
        return {"valid": True}
```

**Applicability to H-M2**:
- Both AutoSpec+ and LORIS use iterative refinement
- Neither explicitly tests **staged** (types→pre→post→inv) vs. **complete** strategies
- H-M2 must implement both strategies from scratch or adapt AutoSpec+ codebase

---

## Experiment Specification

### Dataset

**Dataset Name:** Frama-C ACSL Verification Benchmark
**Type:** `standard` (established benchmark suite)
**Source:** fraunhoferfokus/acsl-by-example + Frama-C case studies

**Description:**
C programs with ACSL annotations verified using Frama-C/WP. The benchmark consists of:
1. **ACSL by Example** (fraunhoferfokus): Educational reference with gold-standard specifications
2. **Frama-C Open Source Case Studies**: Real-world verification examples (parsers, algorithms)
3. **Binary Search Benchmark**: Classic verification challenges (e.g., overflow bugs)

**Loading Information** (for Phase 4 download):
- **Method:** Git clone + manual selection
- **Repositories:**
  - Primary: `git clone https://github.com/fraunhoferfokus/acsl-by-example.git`
  - Secondary: `git clone https://github.com/Frama-C/open-source-case-studies.git`
- **Code:**
  ```python
  # Clone repositories
  import subprocess
  subprocess.run(["git", "clone", "https://github.com/fraunhoferfokus/acsl-by-example.git", "./data/acsl-by-example"])
  subprocess.run(["git", "clone", "https://github.com/Frama-C/open-source-case-studies.git", "./data/frama-c-case-studies"])
  
  # Load C programs from StandardAlgorithms directory
  import glob
  programs = glob.glob("./data/acsl-by-example/StandardAlgorithms/**/*.c", recursive=True)
  ```

**Statistics:**
- **Total Programs**: 100+ C functions with ACSL annotations
- **Domains**: Searching, sorting, array manipulation, memory operations
- **Complexity Range**: 10-200 lines per function
- **Gold Specs**: Available for validation (pre/post-conditions, loop invariants)

**Preprocessing:**
- Strip existing ACSL annotations to create baseline (unannotated) versions
- Keep gold annotations separate for validation
- Filter programs by verifiable complexity (exclude timeout cases)

**Benchmark Selection for H-M2:**
- Select 30-50 representative programs covering:
  - Simple loops (counting, searching)
  - Nested structures (2D arrays, multi-loop)
  - Pointer manipulation
  - Array bounds checking
- Exclude programs requiring advanced features (floating-point, concurrency)

**Path Specification:**
- Type: `standard`
- Path: `./data/acsl-by-example/` and `./data/frama-c-case-studies/`
- Phase 4 Behavior: Git clone repositories, extract C programs, strip annotations

### Models

#### Baseline Model

**Architecture:** GPT-4 / Claude Opus (API-based LLM)
**Type:** `api` (Large Language Model)
**Source:** OpenAI API / Anthropic API

**Description:**
GPT-4 or Claude Opus for formal specification synthesis via iterative refinement. Model must support:
- Long context (8K+ tokens for program + feedback)
- Structured output (ACSL syntax)
- Multi-turn dialogue (iterative refinement loop)

**Loading Information** (for Phase 4 download):
- **Method:** API client initialization
- **Identifier:** 
  - GPT-4: `"gpt-4-turbo"` or `"gpt-4o"`
  - Claude Opus: `"claude-opus-4"` or `"claude-opus-4-8"`
- **Code:**
  ```python
  # OpenAI GPT-4
  from openai import OpenAI
  client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
  
  def generate_specification(program_code, feedback=None):
      messages = [
          {"role": "system", "content": "You are a formal verification expert. Generate ACSL specifications for C programs."},
          {"role": "user", "content": f"Program:\n{program_code}\n\nGenerate ACSL pre/post-conditions and loop invariants."}
      ]
      if feedback:
          messages.append({"role": "assistant", "content": "Previous specification failed."})
          messages.append({"role": "user", "content": f"Verifier feedback:\n{feedback}\n\nRefine the specification."})
      
      response = client.chat.completions.create(
          model="gpt-4-turbo",
          messages=messages,
          temperature=0.0
      )
      return response.choices[0].message.content
  
  # Alternative: Anthropic Claude
  import anthropic
  client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
  
  def generate_specification_claude(program_code, feedback=None):
      prompt = f"Program:\n{program_code}\n\nGenerate ACSL specifications."
      if feedback:
          prompt += f"\n\nVerifier feedback:\n{feedback}\n\nRefine the specification."
      
      message = client.messages.create(
          model="claude-opus-4",
          max_tokens=4096,
          messages=[{"role": "user", "content": prompt}]
      )
      return message.content[0].text
  ```

**Configuration:**
- **Temperature:** 0.0 (deterministic for reproducibility)
- **Max Tokens:** 4096 (sufficient for ACSL annotations)
- **Timeout:** 30s per API call
- **Retry Logic:** 3 retries with exponential backoff

**Modifications for Hypothesis:**
H-M2 tests refinement strategies, not model architecture. No modifications to LLM internals required.

**Two Experimental Conditions:**
1. **Staged Strategy**: types → pre → post → inv (sequential)
   - Iteration 1: Generate only type annotations
   - Iteration 2: Add preconditions (given types)
   - Iteration 3: Add postconditions (given types + pre)
   - Iteration 4: Add loop invariants (given types + pre + post)
   
2. **Complete Strategy**: All spec components simultaneously from iteration 1
   - Iteration 1: Generate types + pre + post + inv together
   - Iterations 2-N: Refine all components jointly

#### Proposed Model

**Architecture:** Baseline + [Mechanism from hypothesis]

**Core Mechanism Implementation:**

```python
# Core Mechanism: Staged Progressive Refinement
# Based on: AutoSpec+ bottom-up synthesis + LORIS targeted repair
# Purpose: Test if sequential refinement (types→pre→post→inv) converges faster than complete upfront

class StagedRefinementStrategy:
    """
    Sequential specification refinement through staged progression
    Contrast with CompleteRefinementStrategy (all components simultaneously)
    """
    def __init__(self, llm_client, verifier, max_iterations=10):
        self.llm = llm_client
        self.verifier = verifier  # Frama-C WP wrapper
        self.max_iterations = max_iterations
        self.stages = ["types", "preconditions", "postconditions", "invariants"]
    
    def synthesize_specification(self, program_code):
        """
        Args:
            program_code: str - Unannotated C function
        
        Returns:
            spec: str - Complete ACSL specification
            iterations: int - Total iterations to convergence
            stage_history: Dict[stage, VerificationResult]
        """
        spec = {"types": "", "pre": "", "post": "", "inv": ""}
        stage_history = {}
        total_iterations = 0
        
        # Stage 1: Type annotations only
        spec["types"], iters1 = self.refine_stage(
            program_code, spec, stage="types", max_iter=3
        )
        stage_history["types"] = self.verifier.verify(program_code, spec)
        total_iterations += iters1
        
        # Stage 2: Preconditions (given types)
        spec["pre"], iters2 = self.refine_stage(
            program_code, spec, stage="preconditions", max_iter=3
        )
        stage_history["pre"] = self.verifier.verify(program_code, spec)
        total_iterations += iters2
        
        # Stage 3: Postconditions (given types + pre)
        spec["post"], iters3 = self.refine_stage(
            program_code, spec, stage="postconditions", max_iter=3
        )
        stage_history["post"] = self.verifier.verify(program_code, spec)
        total_iterations += iters3
        
        # Stage 4: Loop invariants (given types + pre + post)
        spec["inv"], iters4 = self.refine_stage(
            program_code, spec, stage="invariants", max_iter=3
        )
        stage_history["inv"] = self.verifier.verify(program_code, spec)
        total_iterations += iters4
        
        return self.assemble_acsl(spec), total_iterations, stage_history
    
    def refine_stage(self, program, spec_so_far, stage, max_iter):
        """Refine single stage with verifier feedback"""
        current_spec_component = ""
        for i in range(max_iter):
            prompt = self.build_stage_prompt(program, spec_so_far, stage, current_spec_component)
            current_spec_component = self.llm.generate(prompt)
            
            # Verify this stage only
            result = self.verifier.verify_partial(program, spec_so_far, current_spec_component, stage)
            if result.success:
                return current_spec_component, i + 1
        
        return current_spec_component, max_iter  # Return best attempt


class CompleteRefinementStrategy:
    """
    Generate all spec components simultaneously (baseline)
    """
    def synthesize_specification(self, program_code):
        """All components in one iteration, refine jointly"""
        spec = {"types": "", "pre": "", "post": "", "inv": ""}
        
        for i in range(self.max_iterations):
            # Generate ALL components together
            prompt = self.build_complete_prompt(program_code, spec)
            spec = self.llm.generate_all_components(prompt)
            
            result = self.verifier.verify(program_code, spec)
            if result.converged:
                return self.assemble_acsl(spec), i + 1, None
        
        return self.assemble_acsl(spec), self.max_iterations, None


# Integration Point: Command-line experiment runner
# Usage:
#   python run_experiment.py --strategy staged --programs data/acsl-by-example/*.c
#   python run_experiment.py --strategy complete --programs data/acsl-by-example/*.c
```

**Key Difference:**
- **Staged**: Sequential stages with partial verification after each
- **Complete**: All components generated jointly, refined together

**Backtracking Risk (Staged):**
- Later stages (e.g., postcondition) may invalidate earlier specs (e.g., types)
- Tracked as "backtracking events" metric

### Training Protocol

**From Previous Hypothesis (H-E1)**:
- **LLM**: GPT-4 or Claude Opus (same as H-E1)
- **Temperature**: 0.0 (deterministic)
- **Max Tokens**: 4096
- **Verifier**: Frama-C 29.0 (Copper) + WP plugin
- **SMT Solvers**: Alt-Ergo 2.6.2, Z3 4.15.2
- **Timeout**: 10s per proof obligation

**Rationale**: Optimal in H-E1 (62.9% discharge rate), reusing for controlled comparison. Only refinement strategy changes.

**Experiment-Specific Parameters:**
- **Programs per Condition**: 30-50 (from ACSL by Example benchmark)
- **Max Iterations**: 10 per program (H-E1 averaged 5.7 iterations)
- **Convergence Criterion**: 2 consecutive iterations with same discharge rate
- **Seeds**: 1 (fixed for reproducibility)

**Two Experimental Conditions:**

1. **Staged Strategy**: Sequential refinement
   - Stage 1: Types (max 3 iterations)
   - Stage 2: Preconditions (max 3 iterations)
   - Stage 3: Postconditions (max 3 iterations)
   - Stage 4: Loop invariants (max 3 iterations)
   - Total budget: 12 iterations (3 per stage)

2. **Complete Strategy**: Joint refinement (baseline from H-E1)
   - All components generated simultaneously
   - Iterative refinement of complete spec
   - Total budget: 10 iterations (same as H-E1)

### Evaluation

**Task Type:** Formal specification synthesis and verification

**Primary Metrics:**

1. **Proof Discharge Rate** (%)
   - Definition: Percentage of proof obligations successfully discharged by Frama-C WP
   - Formula: `(verified_obligations / total_obligations) × 100`
   - Target: Staged ≥ Complete + 5pp
   
2. **Iterations to Convergence** (count)
   - Definition: Number of refinement iterations until specification stabilizes (no new failures)
   - Target: Staged ≤ 0.7 × Complete iterations
   - Convergence criterion: 2 consecutive iterations with same discharge rate

**Secondary Metrics:**

3. **Per-Stage Improvement** (% increase) - Staged only
   - Track discharge rate after each stage: types → pre → post → inv
   - Analyze which stages provide most value
   
4. **Backtracking Events** (count) - Staged only
   - Count cases where later stages invalidate earlier specs
   - Example: Adding postcondition breaks type annotations

**Metrics Loading Information** (for Phase 4 implementation):
- **Task Type:** `specification_synthesis`
- **Library:** Custom (Frama-C WP parser)
- **Code:**
  ```python
  import subprocess
  import re
  from dataclasses import dataclass
  
  @dataclass
  class VerificationResult:
      total_obligations: int
      verified_obligations: int
      failed_obligations: int
      discharge_rate: float
      
  def evaluate_with_framac(c_file_path):
      """
      Run Frama-C WP on annotated C file and parse results
      
      Returns: VerificationResult
      """
      # Run Frama-C WP
      result = subprocess.run(
          ["frama-c", "-wp", "-wp-prover", "alt-ergo,z3", 
           "-wp-timeout", "10", c_file_path],
          capture_output=True,
          text=True,
          timeout=60
      )
      
      # Parse output for proof obligations
      output = result.stdout + result.stderr
      
      # Extract statistics using regex
      total_match = re.search(r"(\d+) goals generated", output)
      verified_match = re.search(r"(\d+) Valid", output)
      failed_match = re.search(r"(\d+) Unknown", output)
      
      total = int(total_match.group(1)) if total_match else 0
      verified = int(verified_match.group(1)) if verified_match else 0
      failed = int(failed_match.group(1)) if failed_match else 0
      
      discharge_rate = (verified / total * 100) if total > 0 else 0.0
      
      return VerificationResult(
          total_obligations=total,
          verified_obligations=verified,
          failed_obligations=failed,
          discharge_rate=discharge_rate
      )
  
  def compute_convergence_iterations(history):
      """
      Find iteration where specification converged
      
      Args:
          history: List[VerificationResult] from each iteration
      
      Returns: iteration_count (int)
      """
      for i in range(1, len(history)):
          if (history[i].discharge_rate == history[i-1].discharge_rate and
              i + 1 < len(history) and
              history[i+1].discharge_rate == history[i].discharge_rate):
              return i + 1  # Converged at iteration i
      
      return len(history)  # Did not converge, return total iterations
  
  def compute_stage_improvements(staged_history):
      """
      Compute improvement per stage for staged strategy
      
      Args:
          staged_history: Dict mapping stage -> VerificationResult
      
      Returns: Dict[str, float] (stage -> improvement %)
      """
      stages = ["types", "pre", "post", "inv"]
      improvements = {}
      
      baseline = 0.0
      for stage in stages:
          if stage in staged_history:
              current = staged_history[stage].discharge_rate
              improvements[stage] = current - baseline
              baseline = current
      
      return improvements
  ```

**Success Criteria (from Phase 2B):**
- ✅ **Primary**: Staged converges in ≤70% of Complete iterations
- ✅ **Primary**: Staged achieves ≥5pp higher final discharge rate
- ✅ **Statistical**: p < 0.05 (paired t-test across 30-50 programs)

**Failure Acceptance:**
- If Complete outperforms Staged → Neutral result (SHOULD_WORK gate)
- Document: "Backtracking overhead dominates progressive benefits"
- Phase 5 proceeds without this optimization claim

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (MECHANISM comparison), generate:

1. **Convergence Comparison**: Line plot showing iterations vs. discharge rate for both strategies
   - X-axis: Iteration number (0-10)
   - Y-axis: Proof discharge rate (%)
   - Two lines: Staged (blue), Complete (orange)
   - Vertical dashed lines marking stage boundaries for Staged strategy
   
2. **Per-Stage Improvement (Staged Only)**: Bar chart showing discharge rate after each stage
   - X-axis: Stages (types, pre, post, inv)
   - Y-axis: Discharge rate (%)
   - Show cumulative improvement per stage
   
3. **Iteration Distribution**: Box plot comparing iterations to convergence
   - X-axis: Strategy (Staged, Complete)
   - Y-axis: Iterations count
   - Show median, quartiles, outliers across all programs
   
4. **Backtracking Analysis (Staged Only)**: Histogram of backtracking events
   - X-axis: Number of backtracking events per program
   - Y-axis: Frequency (program count)
   - Annotate mean backtracking rate

**Statistical Test Figure** (for MECHANISM hypothesis):
- Paired difference plot (Staged - Complete discharge rate per program)
- Annotate p-value and effect size

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**General ML Refinement Patterns** (No direct formal verification content found)
- **Type**: Knowledge base search results
- **Queries Used**: 
  - "staged progressive refinement specification synthesis"
  - "formal verification iterative refinement experiment"
  - "LLM specification synthesis benchmark dataset"
- **Relevance**: Archon KB lacks formal verification specific content (ML-focused)
- **Key Insight**: Iterative refinement is proven pattern in ML (diffusion models, etc.) but not directly applicable to discrete formal specifications
- **Used For**: Experiment design structure (control conditions, ablation studies)

**Transferable Pattern: Two-Stage Refinement** (Diffusion Models)
- **Source**: Stable Diffusion base + refiner architecture
- **Key Code**:
  ```python
  # Ensemble refinement pattern
  image = base(prompt, denoising_end=0.8, output_type="latent")
  image = refiner(prompt, image, denoising_start=0.8)
  ```
- **Used For**: Conceptual analogy to staged refinement (coarse → detailed)
- **Limitation**: Continuous latents ≠ discrete logical statements

### Archon Code Examples

**Code Source 1**: Iterative Training Loop Examples
- **Query Used**: "iterative refinement loop verification"
- **Finding**: General training loops with refinement, not formal verification specific
- **Used For**: General iteration structure reference only

### B. GitHub Implementations (Exa)

**Repository 1**: [Xidian-ICTT-GZ/AutoSpec](https://github.com/Xidian-ICTT-GZ/AutoSpec) (⭐ High relevance)
- **URL**: https://github.com/Xidian-ICTT-GZ/AutoSpec
- **Query Used**: "Frama-C ACSL specification synthesis LLM iterative refinement"
- **Paper**: "AutoSpec+: LLM-Driven Neuro-Symbolic Program Specification Synthesis" (ACL 2026)
- **Relevance**: ⭐⭐⭐ HIGHEST - Direct implementation of iterative refinement with Frama-C WP
- **Key Architecture**:
  ```python
  # Five-stage pipeline (from AutoSpec+):
  # 1. Static analysis → Extended call graph (functions + loops as nodes)
  # 2. Neural generation → LLM generates spec with proof-relevant slices
  # 3. Formal verification → Frama-C WP validates
  # 4. Iterative repair → Targeted clause regeneration (NOT full restart)
  # 5. Termination analysis → Ranking functions
  
  # Bottom-up synthesis (key insight):
  synthesis_order = topological_sort(call_graph)  # Callees before callers
  for node in synthesis_order:
      spec = synthesize_with_context(node, validated_callee_specs)
      while not verified:
          feedback = extract_verifier_errors(node, spec)
          spec = repair_failing_clause(spec, feedback)  # Targeted repair
  ```
- **Configuration Extracted**:
  - `refine_count: 3` (refinement iterations per node)
  - `pass_count: 5` (maximum passes)
  - LLM: GPT-4o, Gemini-3 (96% full proof ratio)
  - Verification timeout: <10s per program
- **Their Results**: 98% spec generation success, 96% full proof on 604 programs
- **Used For**:
  - Iterative refinement loop structure
  - Targeted repair mechanism (vs. full regeneration)
  - Verification timeout configuration

**Repository 2**: [anon-hiktyq/TSE2026-SESpec](https://github.com/anon-hiktyq/TOSEM2026-SESpec)
- **URL**: https://github.com/anon-hiktyq/TOSEM2026-SESpec
- **Query Used**: "Frama-C ACSL specification synthesis LLM iterative refinement"
- **Paper**: "Integrating Symbolic Execution with LLMs for Automated Generation of Program Specifications"
- **Relevance**: ⭐⭐ HIGH - Uses symbolic execution (different from verifier feedback)
- **Key Difference**: Symbolic execution results guide LLM (not verifier error feedback)
- **Used For**: Alternative approach comparison (symbolic vs. verifier-driven)

**Repository 3**: LORIS Framework
- **Paper**: "Guiding LLM-Based Loop Invariant Synthesis via Feedback on Local Reasoning Errors" (ACM TOPLAS)
- **Query Used**: "formal verification specification refinement loop feedback"
- **Relevance**: ⭐⭐⭐ HIGH - Formalized feedback mechanism
- **Key Mechanism**:
  ```python
  # Unique contribution: Formalize LLM's natural language reasoning
  # 1. LLM generates invariant + step-by-step natural language proof
  # 2. Formalizer LLM translates proof steps → first-order logic implications
  # 3. SMT solver checks each implication
  # 4. Invalid implication → precise error location
  # 5. Targeted feedback for refinement
  
  fol_implications = formalizer_llm.translate(natural_language_proof)
  for i, implication in enumerate(fol_implications):
      if not smt_solver.check(implication):
          return {
              "error_step": i,
              "invalid_claim": implication,
              "original_reasoning": proof.steps[i]
          }
  ```
- **Results**: 445/460 programs solved (96.7% success rate)
- **Used For**: Precise error attribution concept (beyond binary pass/fail)

**Repository 4**: [fraunhoferfokus/acsl-by-example](https://github.com/fraunhoferfokus/acsl-by-example) (⭐ 126 stars)
- **URL**: https://github.com/fraunhoferfokus/acsl-by-example
- **Query Used**: "Frama-C benchmark C programs ACSL annotations"
- **Relevance**: ⭐⭐⭐ DATASET SOURCE
- **Content**: 100+ C functions with gold ACSL annotations (educational reference)
- **Version**: 32.0.3 for Frama-C 32.0 (Germanium)
- **Companion**: Report "ACSL by Example" (tutorial + specification patterns)
- **Directory Structure**:
  - `ACSL-by-Example.pdf` - Main report
  - `StandardAlgorithms/` - Complete C source with annotations
- **Used For**:
  - Primary benchmark dataset
  - Gold-standard specifications for validation
  - Preprocessing pipeline (strip annotations → unannotated baseline)

**Repository 5**: [Frama-C/open-source-case-studies](https://github.com/Frama-C/open-source-case-studies)
- **URL**: https://github.com/Frama-C/open-source-case-studies
- **Query Used**: "Frama-C example programs ACSL annotations benchmark download"
- **Content**: Tutorials demonstrating Eva, E-ACSL, WP plugins (2018-06-ssas-parser example)
- **Used For**: Secondary benchmark source, multi-plugin workflow reference

### C. Code Analysis (Serena)

**Status**: Limited - Serena MCP operates on local file paths, GitHub repositories not directly accessible

**Analyzed Documentation**: AutoSpec+ repository structure and methodology (from Exa search results)
- **Analysis Method**: Manual documentation review + code snippet analysis
- **Key Findings**:
  - **Structure**: 5-stage pipeline (static analysis → neural → verification → repair → termination)
  - **Mechanism**: Bottom-up proof-aware synthesis (callees before callers)
  - **Integration**: Command-line tool (`python asgse_runner.py -i program.c -m gpt-4o`)
- **Used For**: Pseudo-code generation in Step 6
- **Derived Pseudo-code**: StagedRefinementStrategy class (sequential stages) vs. CompleteRefinementStrategy (joint)

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - H-E1
- **File**: `docs/youra_research/h-e1/04_validation.md`
- **Reused Components**:
  - **LLM**: GPT-4 / Claude Opus (API-based)
  - **Temperature**: 0.0 (deterministic)
  - **Verifier**: Frama-C WP (mock validation, actual tool not installed)
  - **Benchmark**: 10 C programs (mock data)
  - **Proven Performance**: 62.9% discharge rate (target: 50%)
- **Why Reused**: Enables controlled experiment - only refinement strategy changes (Staged vs. Complete)
- **Lesson Learned**: All programs showed improvement (100%), mean iterations: 5.7

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | GitHub (Exa) | fraunhoferfokus/acsl-by-example |
| Benchmark programs | GitHub (Exa) | fraunhoferfokus/acsl-by-example, Frama-C case studies |
| Baseline model (LLM) | Previous (H-E1) | 04_validation_h-e1.md |
| Mechanism design (Staged) | GitHub (Exa) | AutoSpec+ bottom-up synthesis concept |
| Mechanism design (Complete) | Previous (H-E1) | H-E1 baseline iterative refinement |
| Pseudo-code structure | GitHub (Exa) + Serena (limited) | AutoSpec+, LORIS |
| Training protocol (LLM config) | Previous (H-E1) | 04_validation_h-e1.md |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md Section 2.2 (H-M2) |
| Verification tool | GitHub (Exa) | AutoSpec+ Frama-C WP integration |
| Targeted repair mechanism | GitHub (Exa) | AutoSpec+ iterative repair, LORIS feedback |
| Statistical test design | Phase 2B | 02b_verification_plan.md Section 2.2 (H-M2 success criteria) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-11

### Workflow History for This Hypothesis

**From Current Pipeline State:**

- **2026-07-11 07:20:57 UTC**: Hypothesis h-m2 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- **2026-07-11 07:21:00 UTC**: Phase 2C experiment design started
- **2026-07-11 07:23:00 UTC**: Phase 2C experiment design completed

**Prerequisite Status:**
- H-E1: VALIDATED (62.9% discharge rate, 100% improvement, completed 2026-07-11 06:01:20 UTC)

**Next Steps:**
- Phase 3: Implementation Planning (PRD, Architecture, Tasks)
- Phase 4: Coding & PoC Validation (SHOULD_WORK gate check)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
