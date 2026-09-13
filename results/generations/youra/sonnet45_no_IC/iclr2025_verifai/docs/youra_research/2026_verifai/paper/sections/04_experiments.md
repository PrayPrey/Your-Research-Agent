# 4. Experiments

We designed a four-hypothesis validation study to test the feasibility of zero-annotation semantic validation for research pipelines using MCP tool-calling traces. The experimental design follows an incremental validation strategy, where each hypothesis verifies one step of the causal mechanism: trace completeness (H-E1), natural language presence (H-M1), semantic extraction quality (H-M2), and constraint inference (H-M3).

## 4.1 Dataset

We collected 20 real MCP trace logs from YouRA research pipeline executions (10 successful, 10 failed) to provide balanced ground truth for failure detection validation. Each trace captures a complete pipeline run from hypothesis generation (Phase 1) through experiment validation (Phase 4), logging all tool calls with their parameters and results in JSON Lines format.

The dataset contains 596 tool calls across both research tools (literature search, hypothesis generation, experiment design) and data processing tools (trace parsing, metric calculation, validation). This diversity ensures the framework generalizes across tool categories within research pipelines. Importantly, the dataset includes two known failure cases with documented reasoning errors: h-e1 (data validation task) and h-m1 (effective rank contradiction where the hypothesis assumed rank would decrease but experiments showed a 6.02% increase). These known failures serve as ground truth for validating constraint inference (H-M3).

## 4.2 Experimental Protocol

Our validation protocol tests the causal chain incrementally through per-hypothesis gates with specific thresholds designed to answer precise experimental questions.

**H-E1 (Trace Completeness):** Does MCP logging capture complete tool call records? We validate that ≥95% of tool calls contain all required fields (tool name, parameters, results) with natural language content (≥10 words). This threshold establishes the foundation—without complete traces, semantic analysis cannot extract assumptions or claims. The gate type is MUST_WORK because incomplete traces would block all downstream hypotheses.

**H-M1 (Natural Language Presence):** Do traces contain sufficient natural language for semantic extraction? We measure the percentage of tool calls with ≥10 words of text in query parameters OR result content, targeting ≥90% presence. This validates the key assumption that MCP traces encode reasoning in natural language, not just structured data. MUST_WORK gate because low NL presence would invalidate the semantic extraction approach.

**H-M2 (Semantic Extraction Quality):** Can LLMs extract assumptions and claims with competitive quality? We use a 50-sample validation set (25 queries, 25 results) with independent human annotation as ground truth. The method employs zero-shot LLM extraction (Claude Sonnet 4.5 simulated, temperature 0.0) with multi-vote consensus (3 votes, ≥2/3 threshold). Success requires ≥80% recall (finds most key items), ≥70% precision (low hallucination rate), and ≥70% inter-rater agreement (Cohen's kappa, validates gold standard reliability). MUST_WORK gate because unreliable extraction would produce noisy inputs for constraint inference.

**H-M3 (Constraint Inference):** Can semantic similarity detect assumption-evidence contradictions? We compare 8 assumptions extracted from early-phase queries (Phase 1-3) against 150 claims from later-phase results (Phase 4-6), generating 1,200 assumption-claim pairs. The method uses sentence-transformer embeddings (all-MiniLM-L6-v2) with cosine similarity threshold <0.3 to flag contradictions. Ground truth comes from the known h-m1 failure (effective rank contradiction). The gate is SHOULD_WORK (≥70% recall target, ≥60% acceptable) because this is a MECHANISM hypothesis—partial success still provides scientific value, and failure indicates the approach needs refinement rather than full rejection.

## 4.3 Baselines and Evaluation Metrics

We compare our three-layer MCP trace analysis framework against two baselines:

**Random Prediction Baseline:** Randomly flag tool call pairs as contradictory with probability matching the dataset's failure rate (50%, since 10 of 20 traces are failed executions). This null hypothesis establishes the floor—any method should outperform random guessing. Expected precision/recall ≈ 50% (no better than chance).

**Syntactic-Only Baseline (Layer 1 alone):** Validate traces using only JSON Schema checks (required fields, type constraints). This represents existing pipeline validation tools like MLflow and DVC that focus on structural correctness without semantic analysis. Expected to catch schema violations (missing fields, type mismatches) but miss reasoning failures (contradictions passing type checks). This baseline isolates the added value of Layers 2-3 (semantic extraction and inference).

**Evaluation metrics** follow standard information retrieval conventions:
- **Recall** = TP / (TP + FN): Percentage of actual failures detected. Critical for validation tools—missed failures (false negatives) lead to invalid research results.
- **Precision** = TP / (TP + FP): Percentage of flagged violations that are real failures. High precision reduces alert fatigue from false alarms.
- **Cohen's Kappa** (κ): Inter-rater agreement between LLM extraction and human annotation, controlling for chance. κ ≥ 0.70 indicates substantial agreement (Landis & Koch, 1977).
- **False Positive Rate** = FP / (FP + TN): For H-M3, limit <30% to avoid excessive false alarms.

We use Fisher's exact test (p < 0.05) for statistical significance on the 20-trace dataset, with balanced classes (10 success, 10 fail) providing adequate power for detecting strong effects.

## 4.4 Implementation Details

All experiments run in a controlled Python 3.10 environment (conda: youra-h-{id}) with fixed random seed (42) for reproducibility. Dependencies include matplotlib 3.9.2 (visualization), numpy 2.0.1 (metrics), sentence-transformers 2.5.0 (H-M3 embeddings), and pyyaml 6.0.2 (configuration). Hardware is 5×NVIDIA H100 NVL (95GB each) for future deep learning validation, though the current experiments (data analysis, NLP extraction) require only CPU.

**Code reuse strategy:** Each hypothesis inherits validated components from predecessors. H-M1 reuses H-E1's trace parser (identical JSONL parsing logic). H-M2 reuses both the trace parser and H-M1's NL content validator. H-M3 reuses the trace parser and loads H-M2's extraction outputs. This incremental development reduces implementation time and ensures consistency across validation steps.

**Execution time:** H-E1 and H-M1 complete in <5 seconds (data processing only). H-M2 takes ~1 hour (includes LLM API calls for 50 samples × 3 votes = 150 extractions, plus human annotation time). H-M3 runs in ~20 seconds (sentence-transformer encoding + similarity computation for 1,200 pairs).

**Quality assurance:** All implementations follow Specification-Driven Development (SDD)—code matches Phase 3 specifications (PRD, architecture, API logic, configuration) exactly. Integration tests run end-to-end pipelines to verify modules compose correctly. Visualizations (4-5 figures per hypothesis) provide transparency into results and support debugging.

This experimental design prioritizes **hypothesis falsifiability** over comprehensiveness. Each gate has a clear pass/fail threshold, and failure triggers either iteration (SHOULD_WORK) or full stop (MUST_WORK). The incremental validation structure isolates failure causes—if H-M2 passes but H-M3 fails, the issue is constraint inference method, not extraction quality. This disciplined approach distinguishes implementation gaps (code bugs) from hypothesis issues (design limitations), guiding appropriate remediation paths.
