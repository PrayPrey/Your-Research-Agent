## 2. Related Work

Our comparison is only interesting if the categories being compared have never been placed side by side. We organize prior work by what its verify stage consumed, and show that each line is individually strong and collectively unable to answer the question we ask.

### 2.1 Execution-Feedback Repair Loops

The dominant paradigm feeds runtime signal back into the prompt. Self-Repair [Olausson et al., 2023] is the closest prior work and the one we replicate as a category: it studies execution-trace feedback on HumanEval and MBPP, reports modest pass@1 gains, and — importantly for us — finds that feedback verbosity matters, with an error trace outperforming a bare pass/fail signal. Reflexion [Shinn et al., 2023] generalizes this to verbal self-reflection, reaching roughly 91% pass@1 on HumanEval with GPT-4. CodeT [Chen et al., 2022] uses model-generated tests as an execution oracle, though for selection among candidates rather than repair, and LEVER [Ni et al., 2023] learns a verifier over execution results. AlphaCode [Li et al., 2022] applies execution filtering at scale.

These establish that the loop works, and Self-Repair's verbosity finding is the specific claim our results complicate. Read as a monotone rule — more feedback text is better — it predicts that Pyright should outperform execution monitoring. We find the opposite, which suggests the finding describes one segment of a curve that turns over. What none of these papers provides is a second category to compare against or a measurement of what the feedback cost: overhead is reported, if at all, as an implementation footnote rather than a denominator.

### 2.2 Generation-Time Correctness Constraints

A parallel line enforces correctness during decoding instead of repairing afterward. Grammar-constrained decoding [Geng et al., 2023] restricts generation to a context-free grammar, and Synchromesh [Poesia et al., 2021] uses constrained sampling for reliable code generation. Both give syntactic guarantees at generation time.

This is a genuinely different paradigm and we do not position against it competitively — constraining decoding and repairing output are complementary. It is worth noting, though, why it cannot substitute for our question: syntactic validity is not the binding constraint in our setting. Among the 126 failures we analyze, 65.9% are logic errors in code that parses, type-checks, and runs without raising. Grammar constraints cannot see those, and neither can any purely syntactic verifier.

### 2.3 Formal and Classical Program Repair

Automated program repair predates LLMs and has a mature formal branch. Gazzola et al.'s survey [Gazzola et al., 2019] covers constraint-based and SMT-guided repair, and Monperrus [Monperrus, 2023] bridges that tradition to the neural era. On the LLM side, AlphaRepair [Xia & Zhang, 2022] and PyDex [Zhang et al., 2023] apply language models to repair tasks directly.

Classical formal repair assumes what LLM benchmarks do not supply: a specification. HumanEval and MBPP ship natural-language docstrings and test suites, not pre- and post-conditions, so applying SMT to them requires synthesizing the specification first. Our design assumed a language model could do that synthesis for roughly 40% of problems. Section 5 reports 6.3%, which we offer as a quantitative bound on where this line of work can currently reach with a GPT-4o-mini-class extractor — a boundary the classical literature has had no occasion to measure because it never had to generate its own specifications.

### 2.4 Benchmarks and Evaluation

HumanEval [Chen et al., 2021] and MBPP [Austin et al., 2021] define the pass@k evaluation protocol our results are reported in, and SWE-bench [Jimenez et al., 2023] extends execution-based evaluation to repository scale. All three report aggregate correctness with no cost dimension, which is appropriate for their purpose and precisely what makes a correctness-only comparison of verifiers misleading: it prices a 9.6-second SMT call identically to a 46-millisecond static analysis call.

### 2.5 Our Position

Every system above chooses a verifier. None compares that choice against the alternatives on fixed conditions, and none reports what the choice cost. We hold the backbone (GPT-4o-mini), the benchmark suite (421 HumanEval and MBPP problems), the prompt template, and the repair budget (3 iterations) fixed, vary only the feedback category across four levels, and measure correctness and wall-clock overhead together. That design is what exposes the two findings prior work could not have seen: that the specificity ordering the field assumes runs backwards, and that the correctness-optimal verifier and the efficiency-optimal verifier are different tools.
