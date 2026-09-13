# Implementation Task List: H-E2 Common Semantic Primitives Across Verifiers

**Date:** 2026-07-11  
**Hypothesis:** H-E2 - Common semantic primitives exist across verifiers (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories  
**Phase:** Phase 3 → Phase 4 Handoff  
**Total Complexity:** 108 points (from 03_architecture.md)  
**Estimated Duration:** 7 weeks (Week 5-12)  

---

## Task Allocation Strategy

Based on 03_architecture.md Epic breakdown (9 major components):

| Component | Complexity | Priority | Dependencies |
|-----------|-----------|----------|--------------|
| A-1: Setup project structure | 8 | P0 (Critical Path) | None |
| A-2: Documentation extractors | 14 | P0 (Critical Path) | A-1 |
| A-3: Empirical extractors | 16 | P0 (Critical Path) | A-1 |
| A-4: Semantic clusterer | 12 | P0 (Critical Path) | A-2, A-3 |
| A-5: Mapping engine | 15 | P0 (Critical Path) | A-4 |
| A-6: Coverage computer | 10 | P0 (Critical Path) | A-5 |
| A-7: Visualizer | 13 | P0 (Critical Path) | A-6 |
| A-8: Pipeline orchestrator | 11 | P0 (Critical Path) | A-7 |
| A-9: Experiment execution | 9 | P0 (Critical Path) | A-8 |

**Total:** 108 complexity points across 9 tasks

---

## Critical Path Tasks (All P0)

### A-1: Setup Project Structure
**Complexity:** 8 points  
**Duration:** 2 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** None  

**Subtasks:**
1. Create project directory structure:
   ```
   taxonomy_builder/
     extractors/
       documentation/    # Web scrapers for docs
       empirical/        # Verifier execution harness
     clustering/         # Semantic primitive identification
     mapping/            # Mapping engine + confidence scoring
     evaluation/         # Coverage computation + visualization
     data/              # Extracted error categories
     results/           # Coverage reports
     figures/           # Visualizations
     config/            # Configuration files
   ```
2. Install dependencies (Python 3.10+, pandas, matplotlib, BeautifulSoup, requests)
3. Create main entry point `taxonomy_builder.py`
4. Setup configuration file `config/config.yaml` (from 03_config.md)
5. Initialize logging system
6. Create README with project structure documentation

**Deliverables:**
- `taxonomy_builder/` directory with all subdirectories
- `requirements.txt` with pinned dependencies
- `config/config.yaml` with verifier settings
- `README.md` with project overview

**Validation Criteria:**
- All directories exist and are properly structured
- `pip install -r requirements.txt` succeeds
- Configuration file is valid YAML
- README documents all major components

---

### A-2: Documentation Extractors
**Complexity:** 14 points  
**Duration:** 4 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** A-1  

**Subtasks:**
1. Implement `FramaCDocExtractor` class:
   - Parse Frama-C WP VC API documentation (https://frama-c.com/api/frama-c-wp/Wp/VC/index.html)
   - Extract VC (Verification Condition) types
   - Extract property categories (assertions, preconditions, postconditions, invariants)
   - Output: `data/framac_doc_errors.json`
2. Implement `DafnyDocExtractor` class:
   - Parse Dafny error documentation (https://dafny.org/v3.12.0/HowToFAQ/Errors)
   - Extract verification failure categories
   - Extract proof obligation types
   - Output: `data/dafny_doc_errors.json`
3. Implement `Why3DocExtractor` class:
   - Parse Why3 Model_parser API (https://why3.org/api/Model_parser.html)
   - Extract error model element types (Error_message, Result, Loop_before, etc.)
   - Extract counter-example categories
   - Output: `data/why3_doc_errors.json`
4. Create unified error category schema (JSON):
   ```json
   {
     "verifier": "frama-c | dafny | why3",
     "category": "error category name",
     "description": "semantic description",
     "source": "documentation | empirical",
     "examples": ["example error messages"]
   }
   ```
5. Implement web scraping with error handling and retry logic
6. Create local documentation snapshots (fallback for offline mode)

**Deliverables:**
- `extractors/documentation/framac_extractor.py`
- `extractors/documentation/dafny_extractor.py`
- `extractors/documentation/why3_extractor.py`
- `data/framac_doc_errors.json`
- `data/dafny_doc_errors.json`
- `data/why3_doc_errors.json`

**Validation Criteria:**
- All extractors run without errors
- Each verifier produces ≥10 error categories from documentation
- JSON output conforms to schema
- Web scraping handles network failures gracefully

---

### A-3: Empirical Extractors
**Complexity:** 16 points (Highest - Verifier installation complexity)  
**Duration:** 5 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** A-1  

**Subtasks:**
1. Install verifiers (use Docker from 03_config.md):
   - Frama-C 28.1
   - Dafny 4.9.0
   - Why3 1.7.2
2. Download benchmark programs:
   - Frama-C examples from official repository
   - Juliet Test Suite verified subset
   - Why3 gallery examples
3. Implement `FramaCEmpiricalExtractor` class:
   - Run Frama-C WP on benchmark programs
   - Capture error messages (stdout, JSON output)
   - Parse error categories from VC failures
   - Collect ≥100 error instances
   - Output: `data/framac_empirical_errors.json`
4. Implement `DafnyEmpiricalExtractor` class:
   - Run Dafny verifier on benchmark programs
   - Capture verification failures
   - Parse error messages and extract categories
   - Collect ≥100 error instances
   - Output: `data/dafny_empirical_errors.json`
5. Implement `Why3EmpiricalExtractor` class:
   - Run Why3 on benchmark programs
   - Capture error model outputs
   - Parse counter-example categories
   - Collect ≥100 error instances
   - Output: `data/why3_empirical_errors.json`
6. Create verifier execution harness with timeout handling
7. Implement error message normalization (remove file paths, line numbers)
8. Create benchmark program selection criteria documentation

**Deliverables:**
- `extractors/empirical/framac_empirical.py`
- `extractors/empirical/dafny_empirical.py`
- `extractors/empirical/why3_empirical.py`
- `data/framac_empirical_errors.json`
- `data/dafny_empirical_errors.json`
- `data/why3_empirical_errors.json`
- `data/benchmark_programs/` (collected programs)
- `Dockerfile` (verifier installation)

**Validation Criteria:**
- All three verifiers install successfully (Docker or native)
- Each verifier produces ≥100 error instances
- Error messages are properly parsed and normalized
- Total error instances across all verifiers ≥500
- Benchmark program selection is documented

---

### A-4: Semantic Clusterer
**Complexity:** 12 points  
**Duration:** 3 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** A-2 (documentation errors), A-3 (empirical errors)  

**Subtasks:**
1. Merge documentation and empirical error categories:
   - Combine `*_doc_errors.json` and `*_empirical_errors.json` per verifier
   - De-duplicate error categories
   - Output: `data/error_categories.json` (unified catalog)
2. Implement semantic clustering algorithm (from 03_logic.md A-2):
   - Extract keywords from error descriptions (proof obligation types)
   - Group by semantic structure (preconditions, postconditions, invariants, etc.)
   - Use rule-based clustering (not ML - deterministic)
3. Generate candidate semantic primitives (≥6 required):
   - MISSING_PRECONDITION
   - POSTCONDITION_FAILURE
   - LOOP_INVARIANT_VIOLATION
   - BOUNDS_CHECK_FAILURE
   - ARITHMETIC_OVERFLOW
   - NULL_DEREFERENCE
   - TERMINATION_FAILURE
   - TYPE_MISMATCH
4. Create semantic primitive definitions:
   ```yaml
   primitive: MISSING_PRECONDITION
   definition: "Function precondition is missing or incomplete"
   keywords: ["precondition", "requires", "pre", "entry"]
   proof_obligation_types: ["precondition", "requires_clause"]
   ```
5. Validate primitives against error category catalog (coverage check)
6. Implement iterative refinement if coverage <60% (expand primitive set)

**Deliverables:**
- `clustering/semantic_clusterer.py`
- `data/error_categories.json` (unified catalog)
- `data/semantic_primitives.yaml` (primitive definitions)

**Validation Criteria:**
- Unified error catalog contains all errors from A-2 and A-3
- ≥6 semantic primitives are generated
- Each primitive has clear definition and keywords
- Preliminary coverage estimate ≥60%

---

### A-5: Mapping Engine
**Complexity:** 15 points  
**Duration:** 4 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** A-4 (semantic primitives)  

**Subtasks:**
1. Implement confidence scoring algorithm (from 03_logic.md A-3):
   - Keyword overlap score (0.0-1.0)
   - Semantic similarity score (definition alignment)
   - Combined confidence score with weights
2. Implement `MappingEngine` class:
   - Load error categories from `data/error_categories.json`
   - Load semantic primitives from `data/semantic_primitives.yaml`
   - For each error category:
     - Compute confidence scores for all primitives
     - Assign best-matching primitive (threshold ≥0.5)
     - Allow multi-primitive assignments if multiple scores >0.7
     - Document tool-specific edge cases (confidence <0.5)
3. Create mapping output schema:
   ```json
   {
     "verifier": "frama-c | dafny | why3",
     "error_category": "category name",
     "semantic_primitive": "PRIMITIVE_NAME | null",
     "confidence_score": 0.0-1.0,
     "notes": "Edge case documentation"
   }
   ```
4. Implement edge case detection and documentation:
   - Categories with confidence <0.5 → unmapped
   - Categories with multiple high scores → multi-primitive
   - Tool-specific categories → document as edge cases
5. Generate mapping table (verifier × category → primitive)
6. Export results to `data/taxonomy_mapping.json`

**Deliverables:**
- `mapping/mapping_engine.py`
- `mapping/confidence_scorer.py`
- `data/taxonomy_mapping.json`

**Validation Criteria:**
- All error categories are processed
- Confidence scores are in valid range [0.0, 1.0]
- Mapping table conforms to schema
- Edge cases are documented with justification

---

### A-6: Coverage Computer
**Complexity:** 10 points  
**Duration:** 3 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** A-5 (taxonomy mapping)  

**Subtasks:**
1. Implement coverage metric computation (from 03_logic.md A-4):
   ```python
   coverage = (mapped_categories / total_categories) × 100%
   ```
2. Implement per-verifier coverage breakdown:
   - Frama-C coverage
   - Dafny coverage
   - Why3 coverage
3. Implement aggregate coverage across all verifiers
4. Implement threshold validation:
   - Aggregate coverage ≥80% (MUST_WORK gate)
   - Per-verifier coverage ≥80% (all three must pass)
5. Generate coverage report JSON:
   ```json
   {
     "aggregate_coverage": 85.2,
     "per_verifier": {
       "frama-c": {"coverage": 87.5, "mapped": 35, "total": 40},
       "dafny": {"coverage": 83.3, "mapped": 25, "total": 30},
       "why3": {"coverage": 84.6, "mapped": 22, "total": 26}
     },
     "gate_status": {
       "aggregate_passed": true,
       "per_verifier_passed": true,
       "overall_passed": true
     },
     "unmapped_categories": [
       {"verifier": "frama-c", "category": "...", "reason": "..."}
     ]
   }
   ```
6. Implement gate status validation
7. Export results to `results/coverage_report.json`

**Deliverables:**
- `evaluation/coverage_computer.py`
- `results/coverage_report.json`

**Validation Criteria:**
- Coverage metrics are computed correctly
- Per-verifier and aggregate coverage are reported
- Gate status is validated against thresholds
- Unmapped categories are listed with reasons

---

### A-7: Visualizer
**Complexity:** 13 points  
**Duration:** 4 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** A-6 (coverage report)  

**Subtasks:**
1. Implement heatmap visualization (from 03_config.md):
   - Rows: Error categories (grouped by verifier)
   - Columns: Semantic primitives
   - Cell values: Confidence scores (color-coded)
   - Export: `figures/taxonomy_heatmap.png`
2. Implement coverage bar chart:
   - Per-verifier coverage bars
   - Threshold line at 80%
   - Export: `figures/coverage_bars.png`
3. Implement error frequency plot:
   - Distribution of error categories per verifier
   - Top 10 most common categories
   - Export: `figures/error_frequency.png`
4. Implement gate comparison visualization:
   - Side-by-side comparison of aggregate vs per-verifier coverage
   - Highlight pass/fail status
   - Export: `figures/gate_comparison.png`
5. Use matplotlib with consistent styling (from 03_config.md):
   - Figure size: 12×8 inches
   - DPI: 300
   - Font: Arial, size 10
   - Color palette: viridis for heatmap, tab10 for bars
6. Create visualization summary document

**Deliverables:**
- `evaluation/visualizer.py`
- `figures/taxonomy_heatmap.png`
- `figures/coverage_bars.png`
- `figures/error_frequency.png`
- `figures/gate_comparison.png`

**Validation Criteria:**
- All four visualizations are generated
- Visualizations match specification (heatmap, bars, frequency, gate)
- Figures are high-resolution (300 DPI)
- Consistent styling across all plots

---

### A-8: Pipeline Orchestrator
**Complexity:** 11 points  
**Duration:** 3 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** A-7 (all components ready)  

**Subtasks:**
1. Implement `TaxonomyBuilder` main class:
   - Initialize all components (extractors, clusterer, mapper, evaluator)
   - Orchestrate pipeline execution in correct order
   - Handle intermediate file I/O
   - Implement error handling and logging
2. Create main execution flow (from 03_architecture.md):
   ```python
   def run_pipeline():
       # Stage 1: Extract error categories
       doc_errors = run_documentation_extractors()
       empirical_errors = run_empirical_extractors()
       
       # Stage 2: Cluster semantic primitives
       primitives = run_semantic_clustering(doc_errors + empirical_errors)
       
       # Stage 3: Construct mapping
       mapping = run_mapping_engine(primitives)
       
       # Stage 4: Compute coverage
       coverage = run_coverage_computer(mapping)
       
       # Stage 5: Generate visualizations
       run_visualizer(coverage, mapping)
       
       return coverage
   ```
3. Implement progress logging (stage completion, file generation)
4. Implement checkpoint system (resume from intermediate stages)
5. Add command-line interface:
   - `python taxonomy_builder.py --full` (run entire pipeline)
   - `python taxonomy_builder.py --stage <stage>` (run specific stage)
   - `python taxonomy_builder.py --config <path>` (custom config)
6. Create orchestrator documentation

**Deliverables:**
- `taxonomy_builder.py` (main entry point)
- `orchestrator/pipeline.py` (orchestration logic)

**Validation Criteria:**
- Pipeline runs all stages in correct order
- Intermediate files are generated and loaded correctly
- Error handling prevents pipeline crashes
- Command-line interface works as specified

---

### A-9: Experiment Execution and Reporting
**Complexity:** 9 points  
**Duration:** 3 days  
**Owner:** Phase 4 Coder  
**Prerequisites:** A-8 (complete pipeline)  

**Subtasks:**
1. Run full pipeline on clean environment:
   - Install all dependencies
   - Download benchmark programs
   - Execute `python taxonomy_builder.py --full`
   - Monitor execution time and resource usage
2. Validate outputs:
   - Verify all data files exist (data/, results/, figures/)
   - Validate coverage report against thresholds
   - Check visualization quality
3. Generate 04_validation.md report (from PRD template):
   - Experiment setup description
   - Data collection statistics (error categories, instances)
   - Taxonomy construction results (semantic primitives)
   - Coverage metrics (per-verifier, aggregate)
   - Gate validation results (MUST_WORK status)
   - Visualizations (embed figures)
   - Edge case analysis (unmapped categories)
   - Discussion of results
   - Conclusion (gate passed/failed)
4. Document reproducibility instructions:
   - Verifier installation steps
   - Benchmark program download
   - Pipeline execution commands
   - Expected outputs
5. Archive all results and code

**Deliverables:**
- `04_validation.md` (experimental results report)
- Complete codebase (`taxonomy_builder/` directory)
- All data files (data/, results/, figures/)

**Validation Criteria:**
- Full pipeline executes without errors
- Coverage ≥80% (MUST_WORK gate passes)
- All required files are generated
- 04_validation.md documents all results
- Reproducibility instructions are clear

---

## Success Criteria Summary

### MUST_WORK Gate Validation
- **Aggregate coverage ≥80%:** Measured in `results/coverage_report.json`
- **Per-verifier coverage ≥80%:** All three verifiers must pass individually
- **Empirical validation:** ≥500 total error instances collected

### Deliverable Checklist
**Phase 3 Outputs (COMPLETED):**
- ✅ 03_prd.md - Product Requirements Document
- ✅ 03_architecture.md - Technical architecture design
- ✅ 03_logic.md - Core logic and algorithms
- ✅ 03_config.md - Configuration schema
- ✅ 03_prp.md - Phase Review Plan
- ✅ 03_implementation_tasks.md - This document

**Phase 4 Expected Outputs:**
- `taxonomy_builder.py` - Main pipeline entry point
- `extractors/` - Documentation + empirical extractors (6 modules)
- `clustering/` - Semantic primitive identification (1 module)
- `mapping/` - Mapping engine + confidence scoring (2 modules)
- `evaluation/` - Coverage computation + visualization (2 modules)
- `orchestrator/` - Pipeline orchestration (1 module)
- `data/` - error_categories.json, semantic_primitives.yaml, taxonomy_mapping.json
- `results/` - coverage_report.json
- `figures/` - 4 visualizations (heatmap, bars, frequency, gate comparison)
- `04_validation.md` - Experimental results + gate validation

---

## Risk Mitigation Reminders

**R1: Coverage Below 80%**
- Monitor coverage after A-6 completion
- Iterate on taxonomy refinement if needed (expand semantic primitives)
- Allow multi-primitive assignments

**R2: Verifier Installation Failures**
- Use Docker containers (Dockerfile in 03_config.md)
- Pin exact verifier versions
- Fallback to documentation-only mode if necessary

**R3: Documentation Parsing Failures**
- Maintain local documentation snapshots
- Supplement with empirical error collection

---

## Archon Integration Notes

**These 9 Epic tasks will be converted to Archon project tasks in Phase 4:**
- Each task (A-1 to A-9) becomes an Archon task with:
  - Title, description, complexity score
  - Dependencies (from table above)
  - Priority (all P0)
  - Expected deliverables
- Progress tracking via Archon MCP tools
- Status updates: todo → doing → review → done

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-11  
**Author:** Phase 3 Implementation Planning Agent  
**Status:** READY FOR PHASE 4  
