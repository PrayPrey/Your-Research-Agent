# Experiment Brief: Dependency-Aware Migration Plans (h-m3)

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Date:** 2026-08-24  
**Prerequisites:** h-e1 (Instrumentation Infrastructure)

---

## 1. Hypothesis Statement

Dependency-aware migration plans reduce breaking changes by 40% and improve adoption rates by ≥ 25% through automated transitive impact analysis.

**Rationale:** Users migrating from deprecated datasets to successors face two key challenges: (1) unforeseen breaking changes in downstream code that depends on the deprecated dataset, and (2) lack of visibility into the full impact radius of the migration. Automated transitive dependency analysis identifies all affected entities (models, pipelines, notebooks) and detects schema/API incompatibilities before migration, reducing runtime failures and increasing user confidence in migration.

---

## 2. Research Questions

1. **Primary:** Does automated dependency graph analysis reduce breaking changes during dataset migration compared to manual migration?
2. **Secondary:** Does providing migration plans with impact analysis increase successor adoption rates?
3. **Tertiary:** What is the completeness of transitive dependency detection in real-world ML codebases?

---

## 3. Variables

### 3.1 Independent Variables (IV)

| Variable | Levels | Operationalization |
|----------|--------|-------------------|
| Migration support | [No plan, Manual plan, Automated plan] | Control: no guidance; Manual: human-written migration guide; Automated: dependency-aware migration plan with transitive impact analysis |
| Dependency complexity | [Low, Medium, High] | Low: 1-2 levels deep; Medium: 3-5 levels; High: 6+ levels |
| Schema compatibility | [Compatible, Minor breaking, Major breaking] | Compatible: drop-in replacement; Minor: field renames/additions; Major: field removals/type changes |

### 3.2 Dependent Variables (DV)

| Variable | Measurement | Target |
|----------|-------------|--------|
| Breaking change rate | % of migration attempts causing runtime errors | Baseline (no plan): 60%, Target (automated plan): ≤ 20% (40% reduction) |
| Successor adoption rate | % of users completing migration within 30 days | Baseline (no plan): 40%, Target (automated plan): ≥ 50% (25% increase) |
| Transitive impact completeness | % of affected entities detected vs. ground truth | ≥ 95% |
| Migration plan accuracy | % of predicted breaking changes matching actual failures | ≥ 80% |

### 3.3 Control Variables (CV)

- Repository platform: HuggingFace Datasets Hub
- Programming language: Python
- Dataset domains: NLP, CV, Audio (diverse schemas)
- User expertise: Mixed (novice to expert)
- Observation period: 6 months

---

## 4. Experimental Design

### 4.1 Design Type

**Randomized Controlled Trial (RCT)** with three groups:
- **Control Group:** Users receive deprecation notice only (no migration plan)
- **Manual Group:** Users receive human-written migration guide (existing best practice)
- **Treatment Group:** Users receive automated dependency-aware migration plan

### 4.2 Participant Allocation

- **Sample size:** 600 users encountering deprecated datasets over 6 months
  - Control: 200 users
  - Manual: 200 users
  - Treatment: 200 users
- **Assignment:** Randomized by user ID hash (deterministic, reproducible)
- **Stratification:** By dependency complexity (Low/Medium/High) to ensure balanced groups

### 4.3 Procedure

#### Phase 1: Dependency Graph Construction (Offline)

1. **Collect usage data:** Mine HuggingFace download logs, GitHub code search, Papers with Code model registry to identify dataset usage relationships
2. **Build dependency graph:** 
   - Nodes: Datasets (deprecated and active)
   - Edges: Usage dependencies (model M uses dataset D, inferred from code)
   - Graph structure: Directed acyclic graph (DAG) or directed graph with cycle detection
3. **Compute transitive closure:** For each deprecated dataset D, identify all transitively dependent entities (models, pipelines, scripts)
4. **Detect schema differences:** Compare deprecated dataset schema vs. successor schema
   - Field-level diff: additions, removals, renames, type changes
   - Compatibility classification: Compatible / Minor breaking / Major breaking

#### Phase 2: Migration Plan Generation (On-demand)

When user loads deprecated dataset:

**Control Group:**
- Display deprecation notice: "Dataset X is deprecated. Consider migrating to Y."
- No additional guidance

**Manual Group:**
- Display deprecation notice + link to human-written migration guide
- Guide content: General migration steps, common pitfalls, manual compatibility checks

**Treatment Group:**
- Display deprecation notice + automated migration plan
- Plan content:
  1. **Impact radius:** List of all transitively affected entities (with counts)
  2. **Breaking changes:** Predicted schema/API incompatibilities with severity scores
  3. **Migration steps:** Ordered task list (update leaf dependencies first, then intermediate, then root)
  4. **Compatibility adapters:** Auto-generated code snippets for minor schema changes
  5. **Verification checklist:** Tests to run post-migration

#### Phase 3: Outcome Measurement (Continuous)

Track via instrumented dataset loaders (from h-e1):
- **Breaking change events:** Runtime errors during migration (exception logs)
- **Adoption events:** User loads successor dataset within 30 days of deprecation notice
- **Bypass events:** User continues using deprecated dataset (no migration attempt)
- **Completion time:** Days from deprecation notice to successful successor adoption

---

## 5. Dataset & Resources

### 5.1 Primary Dataset

**HuggingFace Datasets Hub Metadata + Usage Logs**

- **Type:** Programmatic API (real data)
- **Source:** https://huggingface.co/datasets
- **Size:** ~50,000 datasets (as of 2026-08), ~1,000 with deprecation metadata
- **Features:**
  - Dataset cards (for schema inference, successor relationships)
  - Download logs (for usage velocity, dependency inference)
  - Version history (for schema evolution tracking)
  - Community tags (for task classification)

**Data Collection:**
```python
from datasets import load_dataset_builder
from huggingface_hub import HfApi

api = HfApi()
# List all datasets with deprecation tags
deprecated_datasets = api.list_datasets(tags=["deprecated"])

# For each dataset, extract:
# - Schema (via dataset_info.json)
# - Download counts (via api.dataset_info())
# - Successor links (via README card_data)
# - Usage examples (via community code snippets)
```

### 5.2 Ground Truth Dependency Data

**Papers with Code Model Registry + GitHub Code Search**

- **Purpose:** Identify model-dataset usage relationships (ground truth dependencies)
- **Collection method:**
  - Parse Papers with Code model cards for dataset citations
  - GitHub code search for `load_dataset("dataset_name")` patterns
  - Extract dependency edges: (model_id, dataset_id)

### 5.3 Schema Compatibility Labels

**Manual annotation (one-time):**
- Sample 100 deprecated dataset → successor pairs
- Expert annotators label schema compatibility: Compatible / Minor breaking / Major breaking
- Use as ground truth for schema diff algorithm validation

### 5.4 User Interaction Logs

**From h-e1 instrumentation:**
- Deprecation notice delivery events
- Migration plan view events (Manual/Treatment groups)
- Dataset load events (deprecated vs. successor)
- Runtime error logs (breaking change detection)
- User opt-out events (bypass instrumentation)

---

## 6. Baseline Methods

Since this is a MECHANISM hypothesis testing one component of the overall system, baselines compare migration support strategies:

### 6.1 Baseline 1: No Migration Plan (Control)

**Description:** Status quo deprecation practice
- Display deprecation notice only
- User manually discovers successor via README/community search
- User manually assesses impact and compatibility

**Expected performance:**
- Breaking change rate: 60% (high due to unforeseen incompatibilities)
- Adoption rate: 40% (low due to migration friction)

### 6.2 Baseline 2: Human-Written Migration Guide (Manual)

**Description:** Best-practice manual approach
- Deprecation notice + link to hand-crafted migration guide
- Guide contains general advice, common pitfalls, example code

**Expected performance:**
- Breaking change rate: 45% (reduced via general guidance, but not user-specific)
- Adoption rate: 45% (slightly improved due to clearer guidance)

### 6.3 Proposed Method: Automated Dependency-Aware Plan (Treatment)

**Description:** Novel automated approach
- Deprecation notice + user-specific migration plan
- Plan includes transitive impact analysis, breaking change predictions, ordered migration steps

**Target performance:**
- Breaking change rate: ≤ 20% (40% reduction vs. control via dependency analysis)
- Adoption rate: ≥ 50% (25% increase vs. control via reduced migration friction)

---

## 7. Implementation Strategy

### 7.1 Core Components

#### Component 1: Dependency Graph Builder

**Input:** HuggingFace dataset metadata, GitHub code samples, Papers with Code model cards  
**Output:** Directed graph G = (V, E) where V = datasets, E = usage dependencies  

**Algorithm:**
```python
import networkx as nx

def build_dependency_graph(dataset_metadata, code_samples):
    G = nx.DiGraph()
    
    # Add dataset nodes
    for dataset in dataset_metadata:
        G.add_node(dataset['id'], schema=dataset['schema'])
    
    # Add usage edges from code analysis
    for sample in code_samples:
        dependencies = extract_dataset_loads(sample['code'])
        for dep in dependencies:
            G.add_edge(dep['source_dataset'], dep['dependent_entity'])
    
    return G
```

**Data sources:**
- HuggingFace API: dataset schemas, successor links
- GitHub Code Search: `load_dataset("*")` patterns
- Papers with Code: model-dataset citations

#### Component 2: Transitive Impact Analyzer

**Input:** Dependency graph G, deprecated dataset D  
**Output:** Set of all transitively affected entities  

**Algorithm:**
```python
def compute_impact_radius(graph, deprecated_dataset):
    # Find all descendants (transitive closure)
    affected = nx.descendants(graph, deprecated_dataset)
    
    # Group by entity type (model, pipeline, script)
    impact_summary = {
        'total_affected': len(affected),
        'by_type': categorize_entities(affected),
        'by_depth': compute_depth_distribution(graph, deprecated_dataset, affected)
    }
    
    return affected, impact_summary
```

#### Component 3: Schema Compatibility Detector

**Input:** Deprecated dataset schema S1, successor dataset schema S2  
**Output:** Compatibility classification + breaking change list  

**Algorithm:**
```python
def detect_breaking_changes(schema1, schema2):
    breaking_changes = []
    
    # Field-level diff
    removed_fields = set(schema1.keys()) - set(schema2.keys())
    added_fields = set(schema2.keys()) - set(schema1.keys())
    
    for field in removed_fields:
        breaking_changes.append({
            'type': 'FIELD_REMOVAL',
            'field': field,
            'severity': 'MAJOR'
        })
    
    # Type compatibility check
    for field in set(schema1.keys()) & set(schema2.keys()):
        if schema1[field]['type'] != schema2[field]['type']:
            breaking_changes.append({
                'type': 'TYPE_CHANGE',
                'field': field,
                'old_type': schema1[field]['type'],
                'new_type': schema2[field]['type'],
                'severity': 'MAJOR' if not is_compatible(schema1[field]['type'], schema2[field]['type']) else 'MINOR'
            })
    
    # Classify overall compatibility
    if not breaking_changes:
        classification = 'COMPATIBLE'
    elif all(bc['severity'] == 'MINOR' for bc in breaking_changes):
        classification = 'MINOR_BREAKING'
    else:
        classification = 'MAJOR_BREAKING'
    
    return classification, breaking_changes
```

#### Component 4: Migration Plan Generator

**Input:** Impact radius, breaking changes, dependency graph  
**Output:** Structured migration plan  

**Algorithm:**
```python
def generate_migration_plan(deprecated_dataset, successor_dataset, graph):
    affected, impact_summary = compute_impact_radius(graph, deprecated_dataset)
    compatibility, breaking_changes = detect_breaking_changes(
        get_schema(deprecated_dataset),
        get_schema(successor_dataset)
    )
    
    # Topological sort for migration order (leaf to root)
    migration_order = list(nx.topological_sort(graph.subgraph(affected)))
    
    plan = {
        'impact_radius': impact_summary,
        'compatibility': compatibility,
        'breaking_changes': breaking_changes,
        'migration_steps': generate_steps(migration_order, breaking_changes),
        'compatibility_adapters': generate_adapters(breaking_changes) if compatibility == 'MINOR_BREAKING' else None,
        'verification_checklist': generate_checklist(breaking_changes)
    }
    
    return plan
```

### 7.2 Integration with Instrumentation (h-e1)

Migration plan generation hooks into instrumented dataset loader:

```python
from datasets import load_dataset

def load_dataset_instrumented(dataset_name, **kwargs):
    # Check deprecation status
    if is_deprecated(dataset_name):
        user_group = get_user_group(get_user_id())  # Control/Manual/Treatment
        
        if user_group == 'CONTROL':
            display_deprecation_notice(dataset_name)
        elif user_group == 'MANUAL':
            display_deprecation_notice(dataset_name)
            display_manual_guide(dataset_name)
        elif user_group == 'TREATMENT':
            display_deprecation_notice(dataset_name)
            migration_plan = generate_migration_plan(
                dataset_name,
                get_successor(dataset_name),
                get_dependency_graph()
            )
            display_migration_plan(migration_plan)
        
        # Log event
        log_event('deprecation_notice_shown', {
            'dataset': dataset_name,
            'user_group': user_group,
            'timestamp': now()
        })
    
    # Proceed with actual dataset load
    return load_dataset(dataset_name, **kwargs)
```

---

## 8. Evaluation Metrics

### 8.1 Primary Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Breaking Change Reduction | (BC_control - BC_treatment) / BC_control × 100% | ≥ 40% |
| Adoption Rate Increase | (AR_treatment - AR_control) / AR_control × 100% | ≥ 25% |
| Impact Completeness | TP / (TP + FN) | ≥ 95% |

Where:
- BC = Breaking change rate (% of migrations causing errors)
- AR = Adoption rate (% of users migrating within 30 days)
- TP = True positives (affected entities detected)
- FN = False negatives (affected entities missed)

### 8.2 Secondary Metrics

| Metric | Purpose | Target |
|--------|---------|--------|
| Migration plan accuracy | % of predicted breaking changes matching actual failures | ≥ 80% |
| False positive rate | % of predicted breaking changes that don't occur | ≤ 30% |
| Time to migration | Median days from deprecation notice to successful migration | ≤ 7 days (vs. 14 days baseline) |
| User bypass rate | % of users disabling instrumentation | ≤ 40% (from h-m3 in verification plan) |

### 8.3 Diagnostic Metrics

- **Dependency depth distribution:** Histogram of transitive dependency levels
- **Schema compatibility distribution:** Proportion of Compatible/Minor/Major breaking changes
- **Impact radius distribution:** Size of affected entity sets per deprecated dataset
- **Error type distribution:** Categories of runtime errors (KeyError, TypeError, ValueError)

---

## 9. Success Criteria

### 9.1 MUST_WORK Gate (from verification plan: SHOULD_WORK)

**Correction:** h-m3 has SHOULD_WORK gate per verification plan Section 2.2, not MUST_WORK.

**SHOULD_WORK criteria:**
- Breaking change reduction ≥ 40% (statistical significance p < 0.05)
- Adoption rate increase ≥ 25% (statistical significance p < 0.05)
- Impact completeness ≥ 95%

**If criteria met:** Mechanism validated, proceed to Phase 5 (if enabled)  
**If criteria NOT met:** Partial validation, core system (h-e1, h-m1, h-m2) still valid, migration planning component optional

### 9.2 Statistical Tests

- **Breaking change rate comparison:** Chi-squared test (Control vs. Treatment)
- **Adoption rate comparison:** Chi-squared test (Control vs. Treatment)
- **Impact completeness:** Precision/Recall against ground truth dependency labels

### 9.3 Failure Modes

| Failure Mode | Detection | Mitigation |
|--------------|-----------|------------|
| Dependency graph too sparse | Impact radius < 50% of ground truth | Augment with additional code mining sources |
| Schema diff too noisy | False positive rate > 50% | Add heuristic filters (e.g., ignore added optional fields) |
| User ignores migration plans | View rate < 20% | A/B test plan presentation (popup vs. log message) |
| Breaking change predictions inaccurate | Accuracy < 60% | Incorporate runtime type checking, not just static schema diff |

---

## 10. Timeline & Resources

### 10.1 Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Data collection | 5 days | Dependency graph, schema metadata, ground truth labels |
| Component implementation | 10 days | Graph builder, impact analyzer, schema detector, plan generator |
| Integration with h-e1 | 3 days | Instrumented loader hooks, event logging |
| Pilot testing | 5 days | 50-user pilot, debug edge cases |
| Full deployment | 7 days | 600-user RCT over 6 months (continuous monitoring) |
| Analysis | 5 days | Statistical tests, metric computation, result synthesis |

**Total:** ~35 days (5 weeks) for implementation + 6 months observation

### 10.2 Computational Resources

- **Graph construction:** ~2 GB memory (for 50k dataset graph)
- **Transitive closure:** O(V²) worst case, ~10 seconds per deprecated dataset
- **Schema diff:** O(F) where F = field count, ~100ms per dataset pair
- **Migration plan generation:** ~1 second per user interaction
- **Instrumentation overhead:** < 10% (validated in h-e1)

### 10.3 Data Requirements

- **Dependency graph data:** 500 MB (edges, schemas)
- **User interaction logs:** ~10 GB over 6 months (600 users × 1000 events each)
- **Ground truth labels:** 100 annotated dataset pairs (schema compatibility)

---

## 11. Risks & Mitigations

### 11.1 Data Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| HuggingFace API rate limits | Graph construction fails | Cache metadata, batch requests, use official API key |
| Incomplete usage data | Low dependency graph coverage | Combine multiple sources (GitHub, Papers with Code, HF examples) |
| Schema metadata missing | Cannot compute compatibility | Use heuristics (e.g., infer schema from sample data) |

### 11.2 Experimental Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Too few deprecated datasets | Insufficient sample size | Extend observation period, lower sample size to 300 (100 per group) |
| Users ignore migration plans | Cannot measure adoption impact | A/B test plan presentation, track view vs. ignore rates |
| Breaking changes too rare | Cannot measure reduction | Artificially trigger migrations (ask users to try successor) |

### 11.3 Implementation Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cycle detection in graph | Topological sort fails | Use strongly connected components, break cycles heuristically |
| Schema diff false positives | User distrust in plans | Manual validation on pilot data, tune heuristic thresholds |
| Plan generation latency > 5s | Poor UX | Pre-compute plans offline for known deprecated datasets |

---

## 12. Prior Work & Novelty

### 12.1 Related Work

**Software dependency management:**
- NPM, Maven, pip dependency graphs (well-established)
- Breaking change detection in API evolution (semver, deprecation policies)
- Database schema migration tools (Alembic, Flyway)

**ML dataset versioning:**
- HuggingFace dataset versions (linear versioning, no deprecation lifecycle)
- Data Version Control (DVC) (version tracking, no deprecation support)
- Datasheets for Datasets (documentation, no migration planning)

**Gap:** No existing system combines transitive dependency analysis + schema compatibility detection + automated migration planning for ML datasets.

### 12.2 Novelty Claims

1. **First dependency-aware migration planning for ML datasets:** Existing tools focus on code dependencies (packages), not data dependencies
2. **Automated schema compatibility detection:** Beyond manual documentation, automated field-level diff with breaking change classification
3. **User-specific impact analysis:** Migration plans tailored to user's dependency graph, not generic guides
4. **Quantitative efficacy measurement:** First study measuring breaking change reduction and adoption lift from migration planning

---

## 13. Expected Outcomes

### 13.1 Positive Outcome (Hypothesis Supported)

**Results:**
- Breaking change rate: Control 60%, Manual 45%, Treatment 20% → **67% reduction vs. control**
- Adoption rate: Control 40%, Manual 45%, Treatment 52% → **30% increase vs. control**
- Impact completeness: 97% (missed only indirect dependencies via external APIs)

**Interpretation:**
- Dependency-aware migration planning significantly reduces breaking changes
- Automated impact analysis increases user confidence in migration
- Mechanism validated, supports main hypothesis (50% adoption lift achievable)

**Next steps:**
- Integrate into full system (combine with h-m1, h-m2)
- Extend to other repositories (OpenML, UCI) for generalization

### 13.2 Negative Outcome (Hypothesis Refuted)

**Results:**
- Breaking change rate: Control 60%, Treatment 55% → **Only 8% reduction (not significant)**
- Adoption rate: Control 40%, Treatment 42% → **Only 5% increase (not significant)**

**Possible causes:**
- Dependency graph too sparse (coverage < 50%)
- Schema diff inaccurate (false positive rate > 60%)
- Users don't read migration plans (view rate < 10%)

**Interpretation:**
- Automated migration planning provides marginal benefit over status quo
- Core barriers to adoption are not migration friction (may be user inertia, lack of value in successor)
- Mechanism fails SHOULD_WORK gate, but main hypothesis can still succeed via h-m1 + h-m2 alone

**Pivot options:**
- Focus on high-complexity migrations only (where automated analysis adds most value)
- Improve plan presentation (interactive UI vs. text dump)
- Provide automated migration scripts, not just plans

### 13.3 Partial Outcome

**Results:**
- Breaking change reduction: 40% (meets target)
- Adoption rate increase: 15% (below 25% target)

**Interpretation:**
- Impact analysis successfully reduces errors
- But users still hesitant to migrate (other friction sources: re-training cost, workflow disruption)

**Recommendations:**
- Combine migration plans with compatibility adapters (reduce migration effort)
- Provide automated refactoring tools (update code automatically)
- Study qualitative barriers via user interviews

---

## 14. Archon Knowledge Base Integration

### 14.1 Past Experiment Cases (Inferred - Archon MCP Unavailable)

**[INFERRED]** Dependency graph analysis in software ecosystems
- Source: General knowledge (Archon MCP unavailable)
- Key insights: NPM, Maven use transitive closure for security vulnerability propagation
- Application: Similar algorithm for dataset deprecation impact analysis

**[INFERRED]** Schema evolution in database systems
- Source: General knowledge
- Key insights: ALTER TABLE operations categorized by backward compatibility
- Application: Dataset schema diff with compatibility classification

**[INFERRED]** Breaking change detection in API versioning
- Source: General knowledge (semver, API deprecation studies)
- Key insights: Semantic versioning uses MAJOR.MINOR.PATCH to signal compatibility
- Application: Automated schema diff to classify breaking vs. non-breaking changes

### 14.2 Implementation Resources (Inferred - Exa MCP Unavailable)

**[INFERRED]** Python dependency graph libraries
- Recommended: networkx (standard graph algorithms)
- Use case: Build dependency DAG, compute transitive closure

**[INFERRED]** Schema comparison tools
- Recommended: DeepDiff, jsondiff (Python libraries)
- Use case: Field-level schema diff, type change detection

**[INFERRED]** HuggingFace API patterns
- Recommended: huggingface_hub library
- Use case: Fetch dataset metadata, download logs, dataset cards

---

## 15. Validation Checklist

- [ ] Dependency graph construction validated on sample data (100 datasets)
- [ ] Transitive closure correctness verified against manual inspection
- [ ] Schema diff accuracy measured on ground truth labels (100 dataset pairs)
- [ ] Migration plan generation tested on 10 deprecated datasets
- [ ] Instrumentation integration passes unit tests
- [ ] Pilot study (50 users) shows no critical failures
- [ ] Statistical power analysis confirms 200 users per group sufficient
- [ ] Privacy review confirms telemetry design compliant
- [ ] Performance benchmarks confirm < 10% overhead, < 5s plan generation latency

---

## 16. Deliverables

### 16.1 Code Artifacts

- `dependency_graph.py`: Graph construction from HuggingFace/GitHub/Papers with Code
- `impact_analyzer.py`: Transitive closure, impact radius computation
- `schema_diff.py`: Schema compatibility detection, breaking change classification
- `migration_planner.py`: Plan generation, compatibility adapter synthesis
- `instrumented_loader.py`: Integration with h-e1, event logging

### 16.2 Data Artifacts

- `dependency_graph.json`: Full dependency graph (50k datasets)
- `deprecated_datasets.csv`: List of deprecated datasets with successors
- `schema_metadata.json`: Schema for all datasets
- `ground_truth_labels.csv`: 100 manually annotated schema compatibility labels
- `user_interaction_logs.jsonl`: 6-month telemetry data (600 users)

### 16.3 Analysis Artifacts

- `breaking_change_analysis.ipynb`: Chi-squared tests, effect size calculation
- `adoption_rate_analysis.ipynb`: Survival analysis, time-to-migration curves
- `impact_completeness_report.md`: Precision/Recall on ground truth dependencies

### 16.4 Documentation

- `migration_plan_template.md`: Example generated migration plan
- `user_study_protocol.md`: RCT procedures, consent forms
- `failure_mode_analysis.md`: Edge cases, error handling documentation

---

## 17. References

### 17.1 Prior Work (from Phase 2A)

- Paullada et al. (2021): Data and its (dis)contents survey
- Gebru et al. (2021): Datasheets for Datasets
- NPM/Maven dependency graphs: Software ecosystem deprecation mechanisms

### 17.2 Technical Resources (Inferred)

- NetworkX documentation: Graph algorithms
- HuggingFace Hub API: Dataset metadata access
- DeepDiff: Python schema comparison library

---

## Document Metadata

- **Author:** Phase 2C Experiment Design Pipeline
- **Version:** 1.0
- **Last Updated:** 2026-08-24
- **Hypothesis Status:** IN_PROGRESS → COMPLETED (experiment design)
- **Next Phase:** Phase 3 (Implementation Planning)
