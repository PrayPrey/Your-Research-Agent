# System Architecture Document
# Hypothesis: H-E1 - Documentation Copilot Existence Test

**Version:** 1.0  
**Date:** 2026-04-15  
**Author:** Architecture Agent (TEST mode)  
**Hypothesis ID:** h-e1  
**Hypothesis Type:** EXISTENCE (FOUNDATION)  
**Phase:** 3 - Implementation Planning  

---

## 1. Architecture Overview

### 1.1 System Purpose
Implement an LLM-based documentation copilot that generates contextual suggestions for ML dataset documentation and tracks user acceptance rates to validate the >=70% acceptance hypothesis.

### 1.2 Architecture Pattern
**Pattern:** Request-Response with Logging Pipeline  
**Applied:** Suggestion Generation + User Interaction Tracking (from Archon KB: "AI Assistance Systems with User Feedback Loops")

### 1.3 Hypothesis Context
- **Type:** EXISTENCE (PoC validation)
- **Base Hypothesis:** None (foundation hypothesis)
- **Complexity Tier:** LIGHT (4-8 Epic tasks, 15 total max)
- **Infrastructure:** Minimal (single model, basic logging)

---

## 2. Codebase Analysis (Serena)

**Analysis Status:** GREEN-FIELD (No existing codebase)

**Foundation Hypothesis Context:**
- No base hypothesis to extend
- No existing code to analyze
- Clean slate implementation
- Standard DL experiment structure to follow

**Applied Pattern:** YouRA Standard Structure for ML Experiments
- `src/` for source code
- `data/` for datasets and corpus
- `experiments/` for deployment tracking
- `evaluation/` for metrics calculation

---

## 3. High-Level Architecture

### 3.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                   DOCUMENTATION COPILOT SYSTEM               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐           │
│  │ Example Corpus   │──┐   │  LLM Inference   │           │
│  │ (500+ cards)     │  │   │  (Llama-3-8B)    │           │
│  └──────────────────┘  │   └──────────────────┘           │
│                        │            │                      │
│                        ▼            ▼                      │
│  ┌────────────────────────────────────────┐               │
│  │   Suggestion Generation Engine         │               │
│  │   - Few-shot prompting (3 examples)    │               │
│  │   - Dataset property extraction        │               │
│  │   - Template section targeting         │               │
│  └────────────────────────────────────────┘               │
│                        │                                   │
│                        ▼                                   │
│  ┌────────────────────────────────────────┐               │
│  │   User Interaction Interface           │               │
│  │   - Show suggestion                    │               │
│  │   - Accept/Reject/Modify buttons       │               │
│  └────────────────────────────────────────┘               │
│                        │                                   │
│                        ▼                                   │
│  ┌────────────────────────────────────────┐               │
│  │   Suggestion Tracker                   │               │
│  │   - Log all interactions               │               │
│  │   - Calculate acceptance rate          │               │
│  │   - Store timestamped events           │               │
│  └────────────────────────────────────────┘               │
│                        │                                   │
│                        ▼                                   │
│  ┌────────────────────────────────────────┐               │
│  │   Evaluation Metrics                   │               │
│  │   - Per-user acceptance rates          │               │
│  │   - Stratified analysis                │               │
│  │   - Survey helpfulness scores          │               │
│  └────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
User uploads dataset
    │
    ▼
Extract dataset properties (formats, distributions)
    │
    ▼
Load 3 relevant examples from corpus (by dataset type)
    │
    ▼
Build few-shot prompt (properties + examples + template section)
    │
    ▼
LLM inference (Llama-3-8B, temp=0.7, max_len=500)
    │
    ▼
Display suggestion to user
    │
    ▼
User action: Accept / Reject / Modify
    │
    ▼
Log interaction (suggestion_id, action, timestamp)
    │
    ▼
Calculate acceptance rate (after N suggestions)
    │
    ▼
Evaluate PoC success (>=70% acceptance?)
```

---

## 4. Module Structure

### 4.1 Core Modules

#### Module 1: Corpus Manager (`src/corpus/`)
**Purpose:** Load and manage 500+ high-quality dataset card examples  
**Complexity:** 6/20 (Low)
- File operations: Read markdown files
- Filtering: By dataset type (vision/NLP/tabular)
- Quality check: Completeness score >85%

#### Module 2: Suggestion Generator (`src/copilot/`)
**Purpose:** Generate contextual suggestions using few-shot prompting  
**Complexity:** 14/20 (High)
- Dataset property extraction (formats, distributions, metadata)
- Example selection (3 most relevant from corpus)
- Prompt construction (properties + examples + section)
- LLM inference (transformers pipeline)

#### Module 3: Interaction Tracker (`src/tracking/`)
**Purpose:** Log user interactions and calculate acceptance rates  
**Complexity:** 8/20 (Medium)
- Suggestion logging (ID, text, field, dataset_type, timestamp)
- User action recording (accepted/rejected/modified)
- Acceptance rate calculation
- JSON export for analysis

#### Module 4: Evaluation System (`src/evaluation/`)
**Purpose:** Calculate metrics and validate PoC success  
**Complexity:** 10/20 (Medium)
- Per-user acceptance rate calculation
- Median acceptance across users
- Helpfulness rating aggregation
- Stratified analysis (by dataset type, user experience)
- PoC pass/fail determination

#### Module 5: Deployment Interface (`src/deployment/`)
**Purpose:** Integrate with HuggingFace upload workflow  
**Complexity:** 12/20 (Medium-High)
- Web UI components (suggestion display, action buttons)
- Real-time suggestion generation
- Session management (track user progress)
- Post-session survey collection

---

## 5. File Organization

```
h-e1/
├── src/
│   ├── corpus/
│   │   ├── __init__.py
│   │   ├── loader.py           # Load 500+ example cards
│   │   └── filter.py           # Filter by type and quality
│   ├── copilot/
│   │   ├── __init__.py
│   │   ├── generator.py        # Suggestion generation engine
│   │   ├── property_extractor.py  # Dataset property analysis
│   │   └── prompt_builder.py   # Few-shot prompt construction
│   ├── tracking/
│   │   ├── __init__.py
│   │   ├── tracker.py          # SuggestionTracker class
│   │   └── logger.py           # Interaction logging
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── metrics.py          # Acceptance rate calculation
│   │   └── analysis.py         # Stratified analysis
│   ├── deployment/
│   │   ├── __init__.py
│   │   ├── interface.py        # Web UI integration
│   │   └── survey.py           # Post-session survey
│   └── config.py               # Configuration and hyperparameters
├── data/
│   ├── corpus/
│   │   ├── vision/             # 200 vision dataset cards
│   │   ├── nlp/                # 200 NLP dataset cards
│   │   └── tabular/            # 100 tabular dataset cards
│   └── logs/
│       └── interactions/       # User interaction logs (JSON)
├── experiments/
│   ├── pilot_deployment/
│   │   ├── user_assignments.csv    # Treatment vs control
│   │   └── survey_results.csv      # Helpfulness ratings
│   └── results/
│       ├── acceptance_rates.csv    # Per-user results
│       └── poc_validation.json     # Final PoC pass/fail
├── tests/
│   ├── test_corpus.py
│   ├── test_generator.py
│   ├── test_tracker.py
│   └── test_evaluation.py
└── README.md
```

---

## 6. Epic Tasks

### Epic E-1: Corpus Curation System
**Priority:** 100  
**Complexity:** 6/20 (Module_Size=2 + Dependencies=1 + Algorithm=1 + Integration=2)  
**Type:** data-pipeline  
**Description:** Curate 500+ high-quality HuggingFace dataset cards for few-shot examples

**Subtasks:** None (LIGHT tier - only high complexity modules get subtasks)

**Acceptance Criteria:**
- 500+ dataset cards collected
- Quality filter: Completeness >85%
- Distribution: Vision (200), NLP (200), Tabular (100)
- Stored in structured format (Markdown)

**Files:**
- `src/corpus/loader.py`
- `src/corpus/filter.py`
- `data/corpus/{vision,nlp,tabular}/`

---

### Epic E-2: Suggestion Generation Engine
**Priority:** 95  
**Complexity:** 14/20 (Module_Size=4 + Dependencies=3 + Algorithm=4 + Integration=3)  
**Type:** model  
**Description:** Implement LLM-based suggestion generator with few-shot prompting

**Subtasks:** (High complexity - allocated subtasks)
- E-2-1: Dataset property extraction (analyze file formats, distributions)
- E-2-2: Example selection algorithm (find 3 most relevant examples)
- E-2-3: Prompt construction (build few-shot prompt)
- E-2-4: LLM inference integration (transformers pipeline)

**Acceptance Criteria:**
- Extracts dataset properties from uploaded files
- Selects 3 relevant examples from corpus by dataset type
- Generates suggestion in <2 seconds
- Temperature=0.7, max_length=500 tokens

**Files:**
- `src/copilot/generator.py`
- `src/copilot/property_extractor.py`
- `src/copilot/prompt_builder.py`

---

### Epic E-3: Interaction Tracking System
**Priority:** 90  
**Complexity:** 8/20 (Module_Size=2 + Dependencies=2 + Algorithm=2 + Integration=2)  
**Type:** data-pipeline  
**Description:** Track all user interactions with suggestions for acceptance rate calculation

**Subtasks:** None (Medium complexity - no subtasks in LIGHT tier)

**Acceptance Criteria:**
- Logs every suggestion with unique ID
- Records user action (accepted/rejected/modified)
- Stores timestamps for time-to-decision
- Exports to JSON format

**Files:**
- `src/tracking/tracker.py`
- `src/tracking/logger.py`
- `data/logs/interactions/`

---

### Epic E-4: Evaluation Metrics System
**Priority:** 85  
**Complexity:** 10/20 (Module_Size=3 + Dependencies=2 + Algorithm=3 + Integration=2)  
**Type:** evaluation  
**Description:** Calculate acceptance rate metrics and validate PoC success

**Subtasks:** None (Medium complexity - no subtasks in LIGHT tier)

**Acceptance Criteria:**
- Calculates per-user acceptance rates
- Computes median acceptance across all users
- Aggregates helpfulness ratings from surveys
- Performs stratified analysis (dataset type, user experience)
- Determines PoC pass (>=70% acceptance and >=3.5 helpfulness)

**Files:**
- `src/evaluation/metrics.py`
- `src/evaluation/analysis.py`
- `experiments/results/`

---

### Epic E-5: Pilot Deployment Interface
**Priority:** 80  
**Complexity:** 12/20 (Module_Size=3 + Dependencies=3 + Algorithm=2 + Integration=4)  
**Type:** deployment  
**Description:** Integrate copilot with HuggingFace upload workflow for pilot deployment

**Subtasks:** (Medium-High complexity - allocated subtasks in LIGHT tier)
- E-5-1: Web UI components (suggestion display, action buttons)
- E-5-2: Real-time generation integration
- E-5-3: Session management and survey collection

**Acceptance Criteria:**
- Seamlessly integrated with HuggingFace dataset upload flow
- Real-time suggestion generation
- Intuitive UI for accept/reject/modify
- Post-session survey collection (5-point Likert)
- Supports 50-100 concurrent users

**Files:**
- `src/deployment/interface.py`
- `src/deployment/survey.py`

---

### Epic E-6: Environment Setup and Dependencies
**Priority:** 99  
**Complexity:** 4/20 (Module_Size=1 + Dependencies=1 + Algorithm=1 + Integration=1)  
**Type:** setup  
**Description:** Install required Python packages and configure environment

**Subtasks:** None (Low complexity)

**Acceptance Criteria:**
- All required packages installed (torch, transformers, numpy, pandas, scipy)
- GPU configuration verified (single GPU, CUDA_VISIBLE_DEVICES set)
- Llama-3-8B-Instruct model downloaded

**Files:**
- `requirements.txt`
- `setup.sh`

---

## 7. Task Summary

### 7.1 Epic Task Distribution

| Epic ID | Name | Complexity | Type | Subtasks |
|---------|------|------------|------|----------|
| E-6 | Environment Setup | 4/20 (Low) | setup | 0 |
| E-1 | Corpus Curation | 6/20 (Low) | data-pipeline | 0 |
| E-3 | Interaction Tracking | 8/20 (Medium) | data-pipeline | 0 |
| E-4 | Evaluation Metrics | 10/20 (Medium) | evaluation | 0 |
| E-5 | Deployment Interface | 12/20 (Medium-High) | deployment | 3 |
| E-2 | Suggestion Generator | 14/20 (High) | model | 4 |
| **Total** | **6 Epics** | - | - | **7 subtasks** |

### 7.2 Budget Compliance

**Tier:** LIGHT (15 tasks max, 4-8 epics)

**Task Breakdown:**
- Epic tasks: 6
- Subtasks: 7
- **Total: 13 tasks** ✓ (within 15 max)

**Epic Range:** 6 epics ✓ (within 4-8 range)

### 7.3 Complexity Distribution

| Level | Range | Count | Epic IDs |
|-------|-------|-------|----------|
| Very High | 18-20 | 0 | - |
| High | 14-17 | 1 | E-2 |
| Medium | 9-13 | 2 | E-4, E-5 |
| Low | 4-8 | 3 | E-1, E-3, E-6 |

---

## 8. Integration Points

### 8.1 External Services
- **HuggingFace API:** Dataset upload workflow integration
- **HuggingFace Hub:** Access to Llama-3-8B-Instruct model weights

### 8.2 Internal Dependencies
- Corpus Manager → Suggestion Generator (provides examples)
- Suggestion Generator → Interaction Tracker (logs suggestions)
- Interaction Tracker → Evaluation System (provides acceptance data)
- Deployment Interface → All modules (orchestrates flow)

### 8.3 Data Dependencies
- Example corpus must be curated before suggestion generation (E-1 → E-2)
- Tracking system must be ready before deployment (E-3 → E-5)
- Evaluation system depends on tracked interactions (E-3 → E-4)

---

## 9. Technology Stack

### 9.1 Core Libraries
- **PyTorch:** 2.0+ (LLM inference backend)
- **Transformers:** 4.30+ (Llama-3-8B pipeline)
- **NumPy/Pandas:** Data manipulation and analysis
- **SciPy:** Statistical analysis (binomial proportion test)

### 9.2 Model
- **Base Model:** meta-llama/Llama-3-8B-Instruct
- **Alternative:** GPT-4 API or Claude API (if local inference too slow)
- **Inference:** transformers pipeline with GPU acceleration

### 9.3 Deployment
- **Platform:** HuggingFace (web UI integration)
- **Infrastructure:** Single GPU (V100/A100)
- **Storage:** Local filesystem for logs, JSON for interaction data

---

## 10. Quality Attributes

### 10.1 Performance
- **Suggestion Latency:** <2 seconds per generation
- **System Availability:** 99% uptime during 2-week deployment
- **Throughput:** 50-100 concurrent users

### 10.2 Reliability
- **Data Integrity:** All interactions logged without loss
- **Backup:** Daily backup of interaction logs
- **Error Handling:** Graceful fallback if LLM inference fails

### 10.3 Maintainability
- **Code Structure:** Modular design, clear separation of concerns
- **Testing:** Unit tests for each module (corpus, generator, tracker, evaluation)
- **Documentation:** Inline docstrings, README with setup instructions

---

## 11. Applied Patterns from Archon KB

**Applied:** AI Assistance Systems with User Feedback Loops (Pattern ID: AASUFL-001)
- Core: Suggestion generation → User interaction → Acceptance logging → Metrics calculation
- Rationale: Proven pattern from GitHub Copilot, code completion systems
- Source: Archon Knowledge Base - "LLM-based assistance patterns"

**Applied:** Few-Shot Prompting for Domain-Specific Generation (Pattern ID: FSP-002)
- Core: High-quality examples (500+) + 3-shot prompting
- Rationale: More reliable than zero-shot, faster than fine-tuning for PoC
- Source: Archon Knowledge Base - "LLM prompting strategies"

**Applied:** Stratified Evaluation for User Studies (Pattern ID: SEU-003)
- Core: Acceptance rate by dataset type, user experience level
- Rationale: Reveals which conditions benefit most from assistance
- Source: Archon Knowledge Base - "Human evaluation methodologies"

---

## 12. Risks and Mitigation

### 12.1 Technical Risks
- **Risk:** LLM latency >2s degrades UX
  - **Mitigation:** GPU acceleration, optimize prompt length, cache examples
- **Risk:** Suggestion quality varies by dataset type
  - **Mitigation:** Stratified example corpus (200 vision, 200 NLP, 100 tabular)

### 12.2 Implementation Risks
- **Risk:** Insufficient pilot users (<50)
  - **Mitigation:** Early recruitment, HuggingFace team coordination
- **Risk:** Data logging failures
  - **Mitigation:** Redundant logging, daily backups, validation checks

---

## 13. Next Steps

1. **Phase 3 Continuation:** Generate Logic and Config documents
2. **Phase 4 Implementation:** Follow Epic task order (E-6 → E-1 → E-2 → E-3 → E-4 → E-5)
3. **Phase 4 Validation:** Deploy pilot, collect data, calculate acceptance rate
4. **PoC Decision:** If acceptance >=70% → Continue to H-M1; else STOP

---

**Document Status:** ✅ Complete  
**Next:** Logic Design (03_logic.md), Configuration Design (03_config.md)  
**Architecture Pattern:** Request-Response with Logging Pipeline  
**Task Budget:** 13/15 tasks (LIGHT tier compliant)  
**Generated:** 2026-04-15 (Architecture Agent - TEST mode)
