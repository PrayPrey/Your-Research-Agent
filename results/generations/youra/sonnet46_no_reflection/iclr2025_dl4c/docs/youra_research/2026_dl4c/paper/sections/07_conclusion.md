# 7. Conclusion

We opened by asking whether execution-feedback RL teaches models to think
differently about code structure — concentrating policy movement on control-flow
and data-flow transformations — or simply makes them more confident about
existing surface patterns. Our work provides the first measurement framework
to answer this question rigorously, and delivers a preliminary answer that is
more nuanced than the original hypothesis anticipated.

## 7.1 Summary of Contributions

In this paper, we addressed the absence of structural diagnostic tools in code
generation alignment by introducing **structural efficiency of policy movement**:
semantic AST edit distance per unit KL divergence. Our contributions are:

1. **A formal metric and end-to-end framework** (FA-AST taxonomy + ZSS edit
   distance + KL-matched checkpoints + bootstrap CI + Mann-Whitney testing)
   that runs correctly on real DeepSeek-Coder-7B-instruct-v1.5 checkpoints and
   produces interpretable structural efficiency measurements.

2. **A preliminary empirical finding** showing that GRPO and DPO produce
   nearly identical Semantic Edit Proportions (≈0.237 for both) despite GRPO
   exhibiting substantially higher raw semantic AST edit distances — a
   raw/proportion dissociation that challenges the selective-reallocation
   mechanism and motivates a corrected experimental run.

3. **A documented methodological confound** — checkpoint aliasing — in which
   a nominally 27-pair analysis collapsed to $n_\text{eff} \approx 2$ due to
   insufficient checkpoint diversity, silently corrupting statistical tests.
   We provide a one-assertion safeguard that prevents this failure mode.

## 7.2 Future Directions

**Immediate (required for empirical claims):**
The most pressing next step is a real training run: 1000-step GRPO and DPO
training with `save_steps=100` (yielding 10 diverse checkpoints), real
evalplus-based execution rewards, and execution-oracle DPO pairs. The framework
is ready to analyze these checkpoints. The key open question is whether
SEP_GRPO > SEP_DPO emerges with adequate statistical power, or whether the
dry-run near-equality persists — which would constitute a genuine finding
that GRPO's structural advantage is in total edit volume, not selective
semantic concentration.

**Near-term (mechanism chain):**
If the corrected run confirms SEP_GRPO > SEP_DPO, the full mechanism chain
(H-M2: SEP mediates pass@1; H-M3: SEP negatively correlates with ECE;
H-M4: structural efficiency predicts OOD transfer on LiveCodeBench) becomes
experimentally tractable. The framework handles each downstream analysis with
the same pipeline infrastructure already validated.

**Longer-term (field-wide application):**
Structural efficiency is not limited to GRPO vs. DPO. Any two post-training
methods that produce Python checkpoints can be compared using this framework.
Applying it to instruction tuning, PPO, rejection sampling fine-tuning, and
DPO variants would map out the structural efficiency landscape of code alignment.
At scale, structural efficiency may become a standard diagnostic column alongside
pass@1 in code generation leaderboards.

## 7.3 Closing

The measurement infrastructure is ready. The experiment awaits proper execution.
We hope this framework encourages the code generation community to look beyond
benchmark outcomes and ask, with each new alignment method: not just *what* the
model achieves, but *how* its policy moved to get there.
