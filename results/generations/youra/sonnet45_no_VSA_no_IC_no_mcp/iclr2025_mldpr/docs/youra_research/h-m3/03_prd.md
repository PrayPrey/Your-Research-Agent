# Product Requirements Document: Dependency-Aware Migration Plans (h-m3)

**Hypothesis ID:** h-m3  
**Version:** 1.0  
**Date:** 2026-08-24  
**Status:** Implementation Planning

---

## 1. Executive Summary

### 1.1 Problem Statement

Users migrating from deprecated datasets to successors face unforeseen breaking changes and lack visibility into transitive impact, leading to runtime failures and low adoption rates (baseline: 60% breaking change rate, 40% adoption rate).

### 1.2 Solution Overview

Build automated dependency-aware migration planning system that:
1. Constructs dependency graphs from HuggingFace usage data, GitHub code, Papers with Code
2. Performs transitive impact analysis to identify all affected entities
3. Detects schema compatibility and breaking changes
4. Generates user-specific migration plans with ordered steps and adapters

### 1.3 Success Metrics

| Metric | Baseline | Target | Gate |
|--------|----------|--------|------|
| Breaking change rate | 60% | ≤ 20% (40% reduction) | SHOULD_WORK |
| Adoption rate | 40% | ≥ 50% (25% increase) | SHOULD_WORK |
| Impact completeness | N/A | ≥ 95% | SHOULD_WORK |
| Migration plan accuracy | N/A | ≥ 80% | Secondary |

---

## 2. User Stories

### 2.1 Primary Users

**Persona:** ML practitioner using deprecated HuggingFace dataset

**User Story 1: Impact Visibility**
> As an ML engineer,  
> When I load a deprecated dataset,  
> I want to see all transitively affected models/pipelines/scripts,  
> So that I can assess migration scope before committing.

**Acceptance Criteria:**
- Display impact radius with counts by entity type
- Show dependency depth distribution
- Highlight high-priority affected entities

**User Story 2: Breaking Change Prediction**
> As a data scientist,  
> When I consider migrating to a successor dataset,  
> I want to see predicted schema incompatibilities,  
> So that I can preemptively fix my code.

**Acceptance Criteria:**
- Field-level diff (removals, type changes, renames)
- Severity classification (Compatible/Minor/Major)
- Code snippets for common adapter patterns

**User Story 3: Ordered Migration Path**
> As a team lead,  
> When I plan dataset migration across multiple projects,  
> I want a topologically sorted migration order,  
> So that I update leaf dependencies before root dependencies.

**Acceptance Criteria:**
- Ordered task list (leaf-first)
- Verification checklist post-migration
- Estimated effort per step

---

## 3. Functional Requirements

### 3.1 Dependency Graph Construction

**FR-1.1: Multi-Source Data Collection**
- **Priority:** P0 (Critical)
- **Description:** Collect dataset usage data from HuggingFace API, GitHub Code Search, Papers with Code
- **Input:** Dataset IDs, API credentials
- **Output:** Raw usage relationships (model M uses dataset D)
- **Acceptance Criteria:**
  - HuggingFace: Fetch download logs, dataset cards, version history for 50k datasets
  - GitHub: Search for `load_dataset("*")` patterns across top 10k ML repos
  - Papers with Code: Extract dataset citations from model cards
  - Minimum coverage: 1000 usage edges per deprecated dataset

**FR-1.2: Directed Graph Construction**
- **Priority:** P0 (Critical)
- **Description:** Build dependency graph G = (V, E) where V = datasets, E = usage dependencies
- **Input:** Raw usage data from FR-1.1
- **Output:** NetworkX DiGraph object
- **Acceptance Criteria:**
  - Nodes: Datasets (deprecated + active)
  - Edges: (source_dataset, dependent_entity) with metadata (entity_type, confidence_score)
  - Handle cycles via strongly connected components
  - Serialize to JSON for persistence

### 3.2 Transitive Impact Analysis

**FR-2.1: Impact Radius Computation**
- **Priority:** P0 (Critical)
- **Description:** Compute transitive closure to find all descendants of deprecated dataset
- **Input:** Dependency graph G, deprecated dataset D
- **Output:** Set of affected entities, impact summary
- **Acceptance Criteria:**
  - Use NetworkX `descendants()` for transitive closure
  - Group affected entities by type (model, pipeline, script)
  - Compute depth distribution (levels 1-6+)
  - Performance: < 10s for graphs with 50k nodes

**FR-2.2: Ground Truth Validation**
- **Priority:** P1 (Important)
- **Description:** Measure impact completeness against manually labeled dependencies
- **Input:** 100 ground truth dataset-entity pairs
- **Output:** Precision, Recall metrics
- **Acceptance Criteria:**
  - Recall ≥ 95% (detect at least 95% of true dependencies)
  - Precision ≥ 60% (avoid excessive false positives)

### 3.3 Schema Compatibility Detection

**FR-3.1: Schema Diff Computation**
- **Priority:** P0 (Critical)
- **Description:** Compare deprecated dataset schema vs. successor schema at field level
- **Input:** Schema S1 (deprecated), Schema S2 (successor)
- **Output:** Breaking change list, compatibility classification
- **Acceptance Criteria:**
  - Detect field removals (MAJOR breaking)
  - Detect type changes (MAJOR if incompatible, MINOR if coercible)
  - Detect field renames (heuristic: edit distance < 3)
  - Classify overall: COMPATIBLE / MINOR_BREAKING / MAJOR_BREAKING

**FR-3.2: Compatibility Adapter Generation**
- **Priority:** P1 (Important)
- **Description:** Auto-generate code snippets for MINOR_BREAKING changes
- **Input:** Breaking change list (type: FIELD_RENAME / TYPE_COERCION)
- **Output:** Python code snippets
- **Acceptance Criteria:**
  - Field rename: `dataset = dataset.rename_column("old_name", "new_name")`
  - Type coercion: `dataset = dataset.cast_column("field", "new_type")`
  - Works for 80% of MINOR_BREAKING cases in ground truth

### 3.4 Migration Plan Generation

**FR-4.1: Structured Plan Creation**
- **Priority:** P0 (Critical)
- **Description:** Generate user-specific migration plan with impact, changes, steps
- **Input:** Deprecated dataset D, successor S, dependency graph G
- **Output:** JSON migration plan
- **Acceptance Criteria:**
  - Impact radius section: total count, by-type counts, depth distribution
  - Breaking changes section: list with severity, field, old/new values
  - Migration steps: topologically sorted task list (leaf-first)
  - Compatibility adapters: code snippets for MINOR changes
  - Verification checklist: tests to run post-migration
  - Latency: < 5s per plan

**FR-4.2: Plan Presentation**
- **Priority:** P1 (Important)
- **Description:** Display migration plan in user-facing format
- **Input:** JSON migration plan
- **Output:** Formatted text or HTML
- **Acceptance Criteria:**
  - Collapsible sections (impact / changes / steps)
  - Syntax-highlighted code snippets
  - Priority indicators for high-impact entities

### 3.5 Integration with Instrumentation

**FR-5.1: Loader Hook Integration**
- **Priority:** P0 (Critical)
- **Description:** Hook into instrumented dataset loader from h-e1
- **Input:** Dataset load event (dataset_name, user_id)
- **Output:** Migration plan display (if deprecated), event log
- **Acceptance Criteria:**
  - Check deprecation status via dataset card
  - Assign user to group (Control/Manual/Treatment) via user_id hash
  - Display appropriate intervention (none / manual guide / automated plan)
  - Log event: (user_id, dataset, group, timestamp)
  - Overhead: < 10% (validated in h-e1)

**FR-5.2: Outcome Tracking**
- **Priority:** P0 (Critical)
- **Description:** Track migration outcomes via instrumented events
- **Input:** Dataset load events, error logs
- **Output:** Outcome metrics (breaking changes, adoption, time)
- **Acceptance Criteria:**
  - Track breaking change events (runtime errors during migration)
  - Track adoption events (successor load within 30 days)
  - Track bypass events (continued deprecated usage)
  - Compute metrics per group (Control/Manual/Treatment)

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-1: Latency**
- Graph construction: < 1 hour (offline, one-time)
- Transitive closure: < 10s per deprecated dataset
- Schema diff: < 100ms per dataset pair
- Migration plan generation: < 5s per user interaction

**NFR-2: Scalability**
- Support 50k datasets in dependency graph
- Support 1000 deprecated datasets with successors
- Support 600 concurrent users (RCT sample size)

### 4.2 Reliability

**NFR-3: Data Quality**
- Dependency graph coverage: ≥ 50% of ground truth edges
- Schema diff accuracy: ≥ 80% (validated on 100 labeled pairs)
- Impact completeness: ≥ 95% recall

**NFR-4: Fault Tolerance**
- Handle API rate limits (HuggingFace, GitHub) via caching, retries
- Handle missing schema metadata via heuristics (infer from samples)
- Handle cycles in dependency graph via SCC decomposition

### 4.3 Privacy & Ethics

**NFR-5: User Consent**
- All users in RCT must opt in to instrumentation (from h-e1)
- Opt-out disables event logging and plan generation
- No PII logged (only anonymized user_id hashes)

**NFR-6: Fairness**
- Randomized group assignment ensures balanced confounders
- Stratification by dependency complexity prevents bias

---

## 5. System Architecture

### 5.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User (ML Practitioner)                    │
└────────────────────────────┬────────────────────────────────┘
                             │ load_dataset("deprecated_ds")
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Instrumented Dataset Loader (h-e1)              │
│  - Check deprecation status                                  │
│  - Assign user group (Control/Manual/Treatment)              │
│  - Trigger migration plan generation (if Treatment)          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Migration Plan Generator                    │
│  - Fetch dependency graph                                    │
│  - Compute impact radius (transitive closure)                │
│  - Detect schema compatibility                               │
│  - Generate structured plan                                  │
└────────────────────────────┬────────────────────────────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐
│ Dependency Graph │ │ Schema Diff  │ │ Impact Analyzer │
│     Builder      │ │   Detector   │ │   (NetworkX)    │
│  - HF API        │ │ - DeepDiff   │ │ - Transitive    │
│  - GitHub Search │ │ - Compat.    │ │   closure       │
│  - Papers/Code   │ │   classifier │ │ - Topo. sort    │
└──────────────────┘ └──────────────┘ └─────────────────┘
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                 ┌────────────────────────┐
                 │    Event Logger        │
                 │  - Breaking changes    │
                 │  - Adoption events     │
                 │  - Bypass events       │
                 └────────────────────────┘
```

### 5.2 Data Flow

1. **Offline Phase:**
   - Collect usage data from HF/GitHub/Papers with Code
   - Build dependency graph G, store as JSON
   - Pre-compute schemas for all datasets

2. **Runtime Phase:**
   - User loads deprecated dataset → check deprecation status
   - If Treatment group: generate migration plan
     - Fetch graph from cache
     - Compute impact radius (descendants)
     - Diff schemas (deprecated vs. successor)
     - Generate plan JSON
     - Display formatted plan
   - Log event (deprecation notice shown, plan viewed)

3. **Observation Phase:**
   - Track subsequent dataset loads (successor adoption)
   - Track runtime errors (breaking changes)
   - Aggregate metrics per group

---

## 6. Data Requirements

### 6.1 Input Data

| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| HuggingFace dataset metadata | HF API | ~50k datasets | Graph nodes, schemas |
| Download logs | HF API | ~1M log entries | Usage velocity (for h-m1 integration) |
| GitHub code samples | GitHub Code Search | ~100k snippets | Usage dependencies |
| Papers with Code models | PwC API | ~10k models | Dataset citations |
| Ground truth dependencies | Manual annotation | 100 pairs | Impact completeness validation |
| Ground truth schema labels | Manual annotation | 100 pairs | Schema diff accuracy validation |

### 6.2 Output Data

| Artifact | Format | Size | Purpose |
|----------|--------|------|---------|
| Dependency graph | JSON | ~500 MB | Runtime plan generation |
| Schema metadata | JSON | ~50 MB | Runtime schema diff |
| User interaction logs | JSONL | ~10 GB | Outcome measurement |
| Migration plans (cached) | JSON | ~100 MB | Pre-generated plans for known deprecated datasets |

---

## 7. Implementation Phases

### 7.1 Phase 1: Data Collection (5 days)

**Deliverables:**
- `data_collectors/huggingface_collector.py`: Fetch metadata, logs, schemas
- `data_collectors/github_collector.py`: Search for `load_dataset()` patterns
- `data_collectors/pwc_collector.py`: Extract model-dataset citations
- `dependency_graph.json`: 50k datasets, 100k edges
- `ground_truth_labels.csv`: 100 annotated pairs (impact + schema)

**Dependencies:** HuggingFace API key, GitHub API key

### 7.2 Phase 2: Graph Construction (3 days)

**Deliverables:**
- `graph_builder.py`: Build NetworkX DiGraph from collected data
- `graph_utils.py`: SCC decomposition, cycle handling, serialization
- Unit tests: graph correctness, cycle detection

**Dependencies:** Phase 1 data

### 7.3 Phase 3: Impact Analysis (3 days)

**Deliverables:**
- `impact_analyzer.py`: Transitive closure, depth distribution, grouping
- Ground truth validation script
- Precision/Recall report

**Dependencies:** Phase 2 graph, ground truth labels

### 7.4 Phase 4: Schema Compatibility (4 days)

**Deliverables:**
- `schema_diff.py`: Field-level diff, compatibility classification
- `adapter_generator.py`: Auto-generate code snippets for MINOR changes
- Accuracy validation on ground truth

**Dependencies:** Phase 1 schema metadata, ground truth labels

### 7.5 Phase 5: Migration Plan Generation (3 days)

**Deliverables:**
- `migration_planner.py`: Orchestrate impact + schema + steps generation
- `plan_formatter.py`: JSON → formatted text/HTML
- Latency benchmarks (< 5s)

**Dependencies:** Phase 3 + Phase 4 components

### 7.6 Phase 6: Instrumentation Integration (3 days)

**Deliverables:**
- `instrumented_loader.py`: Hook into h-e1 loader
- User group assignment logic (hash-based randomization)
- Event logging for deprecation notices, plan views

**Dependencies:** Phase 5 planner, h-e1 instrumentation codebase

### 7.7 Phase 7: Testing & Deployment (5 days)

**Deliverables:**
- Unit tests for all components
- Integration tests (end-to-end plan generation)
- Pilot study (50 users, 7 days)
- Bug fixes, edge case handling
- Full RCT deployment (600 users, 6 months)

---

## 8. Risk Management

### 8.1 High-Priority Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| HuggingFace API rate limits | Data collection fails | High | Cache metadata, batch requests, use official API key |
| Dependency graph too sparse | Low impact completeness (< 95%) | Medium | Combine multiple sources (HF + GitHub + PwC), extend collection period |
| Schema diff false positives | User distrust in plans | Medium | Manual validation on 100 pairs, tune heuristic thresholds |
| Users ignore migration plans | Cannot measure adoption impact | Low | A/B test plan presentation (popup vs. log message), track view rates |

---

## 9. Success Criteria & Validation

### 9.1 SHOULD_WORK Gate

**Criteria:**
1. Breaking change reduction ≥ 40% (Treatment vs. Control, p < 0.05)
2. Adoption rate increase ≥ 25% (Treatment vs. Control, p < 0.05)
3. Impact completeness ≥ 95% (Recall on ground truth dependencies)

**Validation:**
- Chi-squared tests for breaking change rate, adoption rate
- Precision/Recall for impact completeness
- Statistical power analysis (200 users per group sufficient)

### 9.2 Secondary Metrics

- Migration plan accuracy: ≥ 80% (predicted breaking changes match actual failures)
- False positive rate: ≤ 30% (avoid alarm fatigue)
- Time to migration: ≤ 7 days median (vs. 14 days baseline)

---

## 10. Stakeholders

| Role | Name/Team | Responsibility |
|------|-----------|----------------|
| Product Owner | h-m3 Implementation Team | Define requirements, prioritize features |
| Researcher | Phase 3 Pipeline | Design experiment, validate hypotheses |
| Engineer (Graph) | TBD | Implement dependency graph construction |
| Engineer (Schema) | TBD | Implement schema diff and adapter generation |
| Data Annotator | TBD | Label 100 ground truth pairs |
| User Researcher | TBD | Conduct pilot study, analyze adoption barriers |

---

## 11. Appendix

### 11.1 Glossary

- **Dependency graph:** Directed graph G = (V, E) where nodes are datasets, edges are usage relationships
- **Transitive closure:** Set of all descendants of a node in a directed graph
- **Schema compatibility:** Classification of breaking changes (Compatible/Minor/Major)
- **Migration plan:** Structured output with impact, changes, steps, adapters, checklist
- **Impact radius:** Number and types of entities transitively affected by deprecation

### 11.2 References

- Experiment Brief: `h-m3/02c_experiment_brief.md`
- Instrumentation Design: `h-e1/` (dependency)
- NetworkX Documentation: https://networkx.org/
- HuggingFace Hub API: https://huggingface.co/docs/huggingface_hub

---

**Document Status:** Ready for Architecture Design  
**Next Step:** Generate `03_architecture.md`, `03_logic.md`, `03_config.md`
