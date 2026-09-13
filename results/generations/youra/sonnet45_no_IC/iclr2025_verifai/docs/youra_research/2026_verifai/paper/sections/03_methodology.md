# 3. Methodology

Our methodology follows directly from the key insight that MCP tool-calling traces encode researcher reasoning in natural language. If traces contain both explicit structure (tool names, parameter types, result schemas) and implicit reasoning (assumptions in query text, evidence in result text), then a three-layer analysis framework should detect semantic failures invisible to syntactic validation. This section describes our architecture, design decisions, and the rationale connecting method to insight.

**Three-Layer Architecture**

Figure 1 illustrates our framework architecture consisting of three sequential layers, each addressing a distinct validation concern:

**Layer 1: Syntactic Structure Validation** checks that MCP traces contain complete records with all required fields (tool name, parameters, result) and validates JSON schemas. This is established technology—we use standard JSON validation libraries and schema compliance checks. Layer 1 answers: "Are traces structurally complete?" Our hypothesis H-E1 tests this with a 95% completeness threshold, hypothesizing that ≥95% of tool calls have all required fields present. This layer provides the foundation for semantic analysis: if traces are incomplete, Layers 2-3 lack data to extract.

**Layer 2: Semantic Query-Parameter Analysis** extracts assumptions from query text using LLM-based NLP. Given a tool call with parameters `{"query": "search for pruning techniques reducing effective rank", "max_results": 10}`, Layer 2 identifies the implicit assumption "effective rank decreases after pruning." We use zero-shot prompting with pre-trained LLMs (Claude Sonnet 4.5 in our implementation) and multi-vote consensus (3 independent extractions, ≥2/3 agreement threshold) to mitigate hallucination. Hypothesis H-M1 validates that ≥90% of tool calls contain ≥10 words of natural language in query parameters, enabling extraction. Hypothesis H-M2 validates extraction quality with thresholds: ≥80% recall (captures most key assumptions), ≥70% precision (low hallucination rate), ≥70% inter-rater agreement (κ≥0.70, confirming gold standard reliability).

**Layer 3: Semantic Result-Content Analysis** extracts evidence from result text using the same LLM-based approach. Given a result containing `{"status": "success", "findings": "Phase 4 validation: effective rank increased 6.02% compared to baseline"}`, Layer 3 extracts the claim "effective rank increased by 6.02%." Hypothesis H-M2 validates extraction for both assumptions (Layer 2) and claims (Layer 3) jointly. The critical step is cross-phase comparison: compare Phase 2-3 assumptions against Phase 4-5 claims to detect mismatches. Hypothesis H-M3 tests constraint inference via semantic similarity matching (cosine distance <0.3 on sentence-transformer embeddings), predicting ≥70% detection recall with <30% false positive rate.

The layered design reflects a key architectural decision: validate foundation before reasoning. Layer 1 must pass (≥95% completeness) before Layer 2 makes sense (cannot extract from missing fields). Layer 2 must pass (≥90% NL presence, ≥80%/70% extraction quality) before Layer 3 can compare assumptions and claims. This dependency structure is intentional—each layer's gate condition validates assumptions required by the next layer.

**Design Decision: Zero-Shot LLM Extraction**

Why use pre-trained LLMs without fine-tuning? Three reasons. First, zero-training constraint from Phase 2A scope definition: our framework must operate without labeled data or model training to satisfy feasibility requirements (researchers cannot annotate thousands of tool calls for every pipeline). Second, pre-trained LLM capability on technical text: models like Claude Sonnet 4.5 and GPT-4 are trained on scientific literature, giving them strong zero-shot extraction for research domain language. Third, multi-vote consensus mitigates hallucination: running three independent extractions and accepting only items appearing in ≥2/3 votes reduces false positives from single-call errors.

Our H-M2 validation (Section 5) confirms this design choice: 82.7% recall and 86.3% precision with substantial inter-rater agreement (κ=0.716) validates that zero-shot extraction achieves competitive quality without annotation overhead. However, this approach has known risks (flagged as Risk R2 in Phase 2B planning): LLM hallucination could introduce false assumptions/claims, reducing precision. We address this via validation against human annotations on a 50-sample test set and report both extraction quality metrics and inter-rater agreement.

**Design Decision: Sentence-Transformer Embeddings for Layer 3**

For constraint inference (Layer 3), we initially chose semantic similarity via sentence-transformers (all-MiniLM-L6-v2 model, 384-dim embeddings, cosine similarity) based on Phase 2A analysis of Neutatz et al.'s constraint enforcement work achieving similar precision. The rationale: if assumption "X decreases" and claim "X increased" discuss the same entity (X) with opposite conclusions, sentence embeddings should capture this as low similarity.

**This approach failed** (H-M3: 0% recall, Section 5). The failure reveals a fundamental mismatch: sentence embeddings optimize for semantic relatedness (topic similarity, paraphrase detection), not logical contradiction. Contradictory statements like "X decreases" and "X increased by 6.02%" have *high* semantic similarity because they discuss the same concept (X, change direction) with shared terminology. The cosine distance is close to 1.0 (very similar), not <0.3 (contradiction threshold).

This negative result is scientifically valuable—it establishes a boundary condition for semantic similarity approaches and narrows the solution space. Section 6 discusses alternative approaches validated by NLI literature: entailment models (BERT-NLI, DeBERTa-MNLI trained on natural language inference tasks) or LLM-based contradiction detection ("Does claim contradict assumption? TRUE/FALSE"). We report the failure transparently and provide threshold tuning analysis (testing 0.2-0.4 range, all achieving 0% recall) to demonstrate the issue is methodological, not threshold calibration.

**Data Collection and MCP Trace Structure**

Our dataset comprises 20 MCP execution traces from the YouRA research pipeline (this pipeline), including 10 successful runs and 10 failed runs. Each trace is a JSONL file where each line represents one tool call:

```json
{
  "tool_name": "rag_search_knowledge_base",
  "parameters": {
    "query": "pruning techniques reducing effective rank",
    "match_count": 5
  },
  "result": {
    "matches": [
      {"title": "SVD-based compression", "relevance": 0.89, 
       "excerpt": "Effective rank increases 3-8% post-compression..."}
    ]
  },
  "timestamp": "2026-07-13T14:23:01Z",
  "phase": 2
}
```

Key fields: `tool_name` (function called), `parameters` (input arguments including text queries), `result` (returned content including findings), `phase` (pipeline stage 1-6). The `parameters.query` and `result.excerpt` fields contain natural language encoding assumptions and evidence respectively.

**Architecture Diagram Description**

Figure 2 shows the end-to-end data flow. MCP traces (JSONL files) enter Layer 1 (TraceParser module, CompletenessValidator) which validates schema compliance and checks field presence. Complete traces proceed to Layer 2 (NLContentValidator, LLMExtractor) which extracts assumptions from query parameters using zero-shot prompts and multi-vote consensus. Simultaneously, Layer 3 (LLMExtractor for results) extracts claims from result content. The SemanticEncoder (Layer 3, sentence-transformers) computes embeddings for assumptions and claims, producing a similarity matrix. The ContradictionDetector filters this matrix with threshold <0.3 to identify mismatches. Finally, the GroundTruthValidator compares detected contradictions against known failures (h-e1, h-m1) to compute precision/recall, and the GateEvaluator checks hypothesis gate conditions.

Each hypothesis (H-E1, H-M1, H-M2, H-M3) tests one layer or component:
- H-E1: Layer 1 completeness (≥95% of tool calls have all required fields)
- H-M1: Layer 2/3 NL presence (≥90% of tool calls have ≥10 words in query AND result)
- H-M2: Layer 2/3 extraction quality (≥80% recall, ≥70% precision, κ≥0.70)
- H-M3: Layer 3 constraint inference (≥70% detection recall, <30% FP rate)

This modular structure enables incremental validation: if H-E1 fails (traces incomplete), subsequent layers are blocked. If H-M2 fails (extraction poor), constraint inference cannot succeed. Our results (Section 5) show H-E1, H-M1, H-M2 passed gates; H-M3 failed, blocking end-to-end validation (H-M4).

**Implementation Details**

All code is implemented in Python 3.9+ with modular architecture matching the three-layer design. Layer 1 uses `json` and `pathlib` for parsing, `regex` for word counting. Layer 2/3 uses Anthropic API (Claude Sonnet 4.5) for extraction with temperature=0.0 (deterministic) and n_votes=3 (multi-vote consensus). Layer 3 uses `sentence-transformers` library (HuggingFace) for all-MiniLM-L6-v2 embeddings and `torch` for cosine similarity computation. Human annotation (H-M2 validation) uses Cohen's Kappa from `scikit-learn` for inter-rater agreement. All hypothesis validation uses Fisher's exact test (p<0.05) for statistical significance where applicable.

Figures are generated using `matplotlib` and `seaborn` at 300 DPI. Each hypothesis produces 4-5 figures: gate metrics (thresholds vs actual), distributions (completeness, word counts, similarity scores), confusion matrices (TP/FP/FN/TN breakdowns), and threshold tuning curves (recall-precision tradeoffs).

**Summary**

Our three-layer architecture operationalizes the key insight that MCP traces encode reasoning in natural language. Layer 1 validates trace completeness (syntactic foundation), Layers 2-3 extract assumptions/claims (semantic extraction), and Layer 3 compares them (constraint inference). Design decisions—zero-shot LLM extraction, multi-vote consensus, sentence-transformer similarity—reflect feasibility constraints (zero annotation) and state-of-the-art capabilities (pre-trained models). The modular structure enables principled failure diagnosis: H-E1, H-M1, H-M2 passed (Layers 1-2 validated), H-M3 failed (Layer 3 requires redesign), providing a clear path forward for fixing constraint inference while preserving validated extraction capabilities.
