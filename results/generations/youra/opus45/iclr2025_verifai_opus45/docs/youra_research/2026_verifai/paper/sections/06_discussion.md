# Discussion

Our results challenge the implicit "more information is better" assumption underlying LLM-based debugging tools. We discuss interpretations, limitations, and implications.

## Why Does Simpler Feedback Work Better?

The dramatic performance advantage of minimal feedback (G0/G1: ~41%) over detailed feedback (G2-G4: ~17-23%) demands explanation. We consider three competing hypotheses:

**Hypothesis 1: Prompt Length Effect (Most Likely)**

G4 prompts can be 10-50× longer than G0 prompts due to full stack traces. Transformer attention may be diluted across the longer input, reducing focus on the actual code that needs repair. The model's effective capacity for reasoning about the code may be consumed by processing error details.

Supporting evidence: The threshold effect at G1→G2 corresponds to adding the error message—the first substantial increase in prompt length beyond a few tokens.

**Hypothesis 2: Cognitive Interference (Plausible)**

Detailed error information may cause the model to "anchor" on specific fix strategies related to the error description, rather than reasoning globally about correctness. A model told "IndexError at line 7" may fixate on line 7 even when the root cause lies elsewhere.

This parallels findings in human debugging: novices often fixate on the error message location while experts consider broader context [citation].

**Hypothesis 3: Model Capacity Limitation (Plausible)**

At 7B parameters, the model may lack the capacity to productively integrate detailed feedback. Larger models (34B, 70B) with greater context processing ability might show different patterns—potentially recovering the expected "more is better" relationship.

This hypothesis is not mutually exclusive with the others; capacity limitations may manifest through the prompt length and anchoring mechanisms.

## The Two-Cluster Pattern

The sharp transition at G1→G2 rather than gradual degradation suggests a qualitative change in model behavior. We hypothesize that:

- **G0/G1 processing:** Model treats the task as "fix this code to pass tests"—a global correctness problem
- **G2+ processing:** Model treats the task as "fix this specific error"—a local repair problem

The global framing may be more effective because it allows the model to reconsider the entire solution approach, while the local framing constrains attention to the error location even when broader changes are needed.

## Relation to Prior Work

Our findings help reconcile apparently conflicting results in the literature:

**Self-Debug [Chen et al., 2023]:** Reported 12% improvement on MBPP using G2-level feedback. Our G2 achieves 18.4%, broadly consistent. However, Self-Debug did not compare against G0—if they had, they might have found even better results with simpler feedback.

**Haque et al. [2025]:** Found that execution traces "provide limited improvement" for LLM repair unless prompts are LLM-optimized. This aligns with our observation that detailed traces (G4) underperform minimal feedback (G0). Their finding was descriptive; we provide the controlled comparison quantifying the effect.

**TraceFixer, DynaFix:** These approaches use G4+ feedback for larger models or different task distributions. Our results do not contradict their findings but suggest their approaches may not transfer to smaller models on simpler tasks.

## Limitations

We acknowledge several limitations that scope our conclusions:

**L1: Single Model Tested**

Our results are specific to CodeLlama-7B-Instruct. Larger models (13B, 34B, 70B) may show different patterns—potentially recovering the expected benefit of detailed feedback. We frame our contribution as establishing the phenomenon at the 7B scale; scaling studies are needed to determine where the crossover occurs.

**L2: Single Benchmark**

MBPP consists of relatively simple single-function problems. Complex multi-file debugging may show different granularity effects. However, MBPP is the standard benchmark in this literature, enabling comparison with prior work.

**L3: Single Prompt Template**

We use the Self-Debug template throughout. Template-granularity interactions are possible—a template optimized for detailed feedback might recover some performance. We note this as future work while observing that Self-Debug is the established baseline.

**L4: Single Repair Attempt**

We evaluate single-turn repair. Multi-turn iterative repair might show different patterns, potentially starting with G0 and escalating to detailed feedback on failure. Adaptive strategies remain unexplored.

**L5: Deterministic Generation**

Temperature 0 ensures reproducibility but may not represent deployment conditions where sampling (T > 0) is used. Stochastic generation with multiple samples might show different granularity effects.

**L6: Runtime Errors Only**

We focus on runtime errors (60.8% of failures). Silent logic errors producing wrong outputs may respond differently to granularity variations.

## Implications for Practice

Our findings suggest practical guidelines for LLM-based debugging tools:

1. **Scale-Aware Feedback:** Tools should consider model size when selecting feedback granularity. For 7B-scale models, simpler feedback may be more effective.

2. **Adaptive Strategies:** Rather than fixed granularity, tools might start with minimal feedback and escalate only if initial repair fails.

3. **Evaluation Methodology:** Future work should include granularity ablations rather than assuming a fixed feedback level is optimal.

## Broader Impact

**Positive Impacts:** Our findings may improve LLM-based coding assistants by informing feedback design. Simpler, more effective repair prompts could reduce computational costs and improve user experience.

**Potential Concerns:** We do not identify significant negative impacts from this research. The findings apply to debugging tools, which have limited dual-use potential.

**Reproducibility:** All experiments use publicly available models (CodeLlama) and benchmarks (MBPP). We report all hyperparameters and statistical procedures to enable replication.
