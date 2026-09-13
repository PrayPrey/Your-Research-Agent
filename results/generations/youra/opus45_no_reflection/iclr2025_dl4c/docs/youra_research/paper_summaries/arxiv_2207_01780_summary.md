---
source_paper: "arxiv_2207_01780.md"
generated_at: "2026-08-18T13:31:31.235804"
model: "openai/gpt-5.2"
summary_chars: 12626
---

# CodeRL: Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning

## Key Metadata
- **Authors:** Hung Le et al.
- **Year:** 2022
- **Venue:** arXiv
- **Core Contribution:** An actor–critic RL framework (“CodeRL”) that optimizes pretrained code LMs for *functional correctness* using unit-test-driven rewards plus a critic-based dense token-level signal, and a test-time “critic sampling” procedure that refines/repairs programs using example tests.

## Section Summaries

### Abstract
Program synthesis or code generation aims to generate a program that satisﬁes a
problem speciﬁcation. Recent approaches using large-scale pretrained language
models (LMs) have shown promising results, yet they have some critical limitations.
In particular, they often follow a standard supervised ﬁne-tuning procedure to train a
code generation model only from the pairs of natural-language problem descriptions
and ground-truth programs. Such paradigm largely ignores some important but
potentially useful signals in the problem speciﬁcation such as unit tests, which
thus often results in poor performance when solving complex unseen coding tasks.
To address the limitations, we propose “CodeRL”, a new framework for program
synthesis tasks through pretrained LMs and deep reinforcement learning (RL).
Speciﬁcally, during training, we treat the code-generating LM as an actor network,
and introduce a critic network that is trained to predict the functional correctness
of generated programs and provide dense feedback signals to the actor. During
inference, we introduce a new generation procedure with a critical sampling strategy
that allows a model to automatically regenerate programs based on feedback from
example unit tests and critic scores. For the model backbones, we extended the
encoder-decoder architecture of CodeT5 with enhanced learning objectives, larger
model sizes, and better pretraining data. Our method not only achieves new SOTA
results on the challenging APPS benchmark, but also shows strong zero-shot
transfer capability with new SOTA results on the simpler MBPP benchmark.

### Introduction & Motivation
Program synthesis models trained with standard next-token prediction (teacher forcing) suffer from exposure bias and optimize token-level likelihood rather than *functional correctness*, so token similarity metrics (e.g., BLEU) correlate poorly with whether code passes tests. Existing LM-based synthesis methods also underuse unit tests (often included as example I/O in problem statements) during both training and inference, typically using them only for candidate filtering/ranking. The paper targets complex, competition-style tasks (e.g., APPS) where these shortcomings are amplified. CodeRL is proposed to align optimization and generation with unit-test outcomes via RL plus critic-guided regeneration/repair at inference time.

### Methodology
CodeRL formulates program synthesis as RL where a pretrained LM policy \(p_\theta\) (actor) generates a program token-by-token given problem description \(D\). Supervised fine-tuning uses cross-entropy:
\[
L_{\text{ce}}(\theta)=-\sum_t \log p_\theta(w_t|w_{1:t-1},D). \tag{1}
\]
RL fine-tuning minimizes negative expected return:
\[
L_{\text{rl}}(\theta)=-\mathbb{E}_{W^s\sim p_\theta}[r(W^s)], \tag{2}
\]
with REINFORCE gradient:
\[
\nabla_\theta L_{\text{rl}} \approx -\mathbb{E}_{W^s}[r(W^s)\nabla_\theta \log p_\theta(W^s|D)] \approx -\mathbb{E}_{W^s}\left[r(W^s)\sum_t \nabla_\theta \log p_\theta(w_t^s|w_{1:t-1}^s,D)\right]. \tag{3}
\]
Return \(r(W^s)\) is derived from unit-test outcome (compiler+tests): CompileError \(-1.0\), RuntimeError \(-0.6\), FailedTest \(-0.3\), PassedTest \(+1.0\) (Eqs. 4–7). To reduce variance, they subtract a greedy-decoding baseline \(W^b\):
\[
\nabla_\theta L_{\text{rl}} \approx -\mathbb{E}_{W^s}\left[(r(W^s)-r(W^b))\sum_t \nabla_\theta \log p_\theta(w_t^s|w_{1:t-1}^s,D)\right]. \tag{8}
\]
They further densify feedback with a **critic** \(p_\phi(u|W^s,D)\) trained (supervised) to predict the 4-way unit-test outcome:
\[
L_{\text{critic}}(\phi)=-\log p_\phi(u|W^s,D). \tag{9}
\]
Architecturally, critic is a smaller Transformer seq2seq model than the actor (CodeT5-small critic for CodeT5 actors; GPT2-small critic for GPT actors). The critic max-pools decoder hidden states \(h_{1:T}\) to predict \(u\), but also uses token-level hidden state \(h_t\) to estimate a per-token “value” \(\hat q_\phi(w_t^s)=\hat v_t[u]\) where \(\hat v_t=\text{softmax}(\text{Linear}(h_t))\). Actor update becomes:
\[
\nabla_\theta L_{\text{rl}} \approx -\mathbb{E}_{W^s}\left[(r(W^s)-r(W^b))\sum_t \hat q_\phi(w_t^s)\nabla_\theta \log p_\theta(w_t^s|w_{1:t-1}^s,D)\right]. \tag{10}
\]
Training schedule: (i) imitation warm-start with \(L_{\text{ce}}\) up to 10 epochs; (ii) sample synthetic programs from frozen actor to train critic (also include ground-truth programs labeled PassedTest); (iii) fine-tune actor with combined \(L_{\text{ce}}\) and \(L_{\text{rl}}\) (equal weights), using a single Monte Carlo sample per step:
\[
\nabla_\theta L_{\text{rl}} \approx -(r(W^s)-r(W^b))\sum_t \hat q_\phi(w_t^s)\nabla_\theta \log p_\theta(w_t^s|w_{1:t-1}^s,D). \tag{14}
\]

**Backbone model improvements (CodeT5 extension):** they pretrain CodeT5-large (770M) from scratch with (a) larger Python data **GCPY** (10.5B tokens; 10× larger than CodeSearchNet) and (b) add **next-token prediction (NTP)** pretraining in addition to masked span prediction (MSP): sample a pivot (10%–90%) so encoder sees prefix and decoder predicts suffix, reducing mismatch to synthesis. Pretraining setup: 16×A100-40GB; ~21 days total. MSP stage: corruption 15%, peak LR \(2\cdot 10^{-4}\), batch 2048, CSN 150 epochs then GCPY 10 epochs. NTP stage: peak LR \(10^{-4}\), batch 256, 10 epochs; max lengths source 768 / target 600. Optimizer AdamW, weight decay 0.05, linear decay with 1000 warmup steps.

**Inference: Critic Sampling (CS)** leverages example unit tests embedded in prompt. Generate \(N=200\) programs via nucleus sampling; run example tests → set \(P\) (passed) and \(F\) (failed). If \(P\neq\emptyset\), **program refining**: a binary critic \(\phi_{\text{test}}\) (PassedTest vs FailedTest) scores prefixes
\[
\hat q_{\phi_{\text{test}}}(w_t)=p_{\phi_{\text{test}}}(\text{PassedTest}\mid w_{1:t},D), \tag{11}
\]
select split at \(t_{\max}\) (highest score), optionally chop earlier if prefix becomes more “failed” than “passed”, then regenerate suffix conditioned on this seed (upsample seeds \(N/|P|\)). If \(P=\emptyset\), **program repairing**: score whole failed programs
\[
\hat q_{\phi_{\text{test}}}(W^{\text{fail}})=p_{\phi_{\text{test}}}(\text{PassedTest}\mid W^{\text{fail}},D), \tag{12}
\]
take top \(M\) candidates and feed them (plus error type/subtype and compiler messages) into a seq2seq repair model \(\omega\) trained with:
\[
L^{\text{repair}}_{\text{ce}}(\omega)=-\sum_t \log p_\omega(w_t\mid w_{1:t-1},D,W^{\text{fail}},u,c). \tag{13}
\]
They run at most one round of refine/repair in practice.

### Experiments & Results
**Benchmarks.**  
(1) **APPS** (10,000 problems; 50/50 train-test). Avg 23.2 correct Python solutions and 21.2 unit tests/problem; avg problem length 293.2 words; avg program length 18.0 lines. Difficulty splits: Intro 3639 (train/test 2639/1000), Interview 5000 (2000/3000), Competition 1361 (361/1000).  
(2) **MBPP** (974 problems; 374/90/500 train/val/test; +10 few-shot reserved). Each problem has 1 solution (~6.8 lines) and 3 assert tests included in the prompt.

**Metrics.** pass@k (Hendrycks et al. 2021) for \(k\in\{1,5,1000\}\). Also n@k (Li et al. 2022): filter to \(n\) candidates from \(k\) using example tests; report 1@k and 5@k. CodeRL limits inference CS to one round; nucleus sampling with \(N=200\) for CS.

**Baselines.** GPT2, GPT-Neo, GPT-J, GPT3 (Brown et al. 2020), Codex (Chen et al. 2021a), AlphaCode (Li et al. 2022). Most baselines are APPS-finetuned with \(L_{\text{ce}}\) only (except Codex/GPT3 few-shot).

**Main APPS results (Table 1).** CodeRL+CodeT5 (770M) achieves new SOTA on pass@k: **2.69 pass@1**, **6.81 pass@5**, **20.98 pass@1000** (All). It also attains **8.48 1@1000** and **12.62 5@1000** on filtered n@k. Notably, with \(k=1000\) it is competitive with AlphaCode at \(k=50000\) (compute-budget efficiency claim).

**Compact results table (APPS, All):**

| Model | Size | pass@1 | pass@5 | pass@1000 | 1@1000 | 5@1000 |
|---|---:|---:|---:|---:|---:|---:|
| Codex | 12B | 0.14 | 0.51 | 7.87 | 2.64 | 7.46 |
| AlphaCode | 1B | – | – | 8.09 | – | 7.17 (k=1000) / 11.42 (k=50000) |
| GPT3 | 175B | 0.03 | – | – | – | – |
| GPT-J | 6B | 1.86 | 4.95 | 17.63 | – | – |
| **CodeRL+CodeT5** | **770M** | **2.69** | **6.81** | **20.98** | **6.78** | **12.62** |

**Ablations (training returns; Table 2).** Best is relative return with baseline + learned critic token values (Model D): All **1.50 pass@1**, **1.90 pass@5** under beam-search ablation settings; absolute return without baseline hurts most (Model B). Critic-free identical token reward (Model A) underperforms; heuristic linear-decay token weights (Model C) < learned critic.

**Ablations (loss terms; Table 3).** Using only \(L_{\text{rl}}\) after warm-start degrades (vanishing gradients); using only \(L_{\text{ce}}\) can overfit and reduce test performance. Best is combined \(L_{\text{ce}}+L_{\text{rl}}\), e.g., for CodeT5-770M: All **2.28 pass@1**, **3.10 pass@5** (ablation setting), improving over other combinations; similar trends on GPT-Neo.

**Inference ablation: Critic Sampling (Table 4).** On CodeT5, CS improves especially large-k metrics. With both refining + repairing and \(M=1\): All **14.38 pass@200** vs 12.12 (no CS); All **20.98 pass@1000** vs 17.78; All **6.78 1@1000** vs 6.00. Larger \(M\) can slightly hurt (less upsampling per candidate).

**Pretraining ablation (Table 5).** Scaling + data + objective matter: CodeT5-770M with CSN+GCPY and MSP+NTP improves All pass@5 from **2.06 → 2.90** and All pass@1 from **1.56 → 2.00** (still \(L_{\text{ce}}\)-only fine-tuning for fairness in this ablation).

**MBPP zero-shot transfer (Table 6).** CodeRL+CodeT5 trained on APPS and evaluated zero-shot on MBPP achieves **63.0% pass@80**, exceeding finetuned GPT-137B **61.4% pass@80** (Austin et al. 2021 prompt format). They analyze overlap APPS↔MBPP and report minimal duplication (e.g., 12.6% MBPP programs have >50% lines duplicated in APPS training).

**Compute cost (reported).** CodeT5-large pretraining: ~21 days on 16×A100-40GB. APPS warm-start fine-tuning: ~30 hours on 1×A100 for 10 epochs. MBPP fine-tuning: <30 minutes on 1×A100.

### Discussion & Conclusion
CodeRL improves program synthesis by aligning training and inference with unit-test-based functional correctness, using an actor–critic setup where the critic provides dense token-level guidance and a baseline reduces variance. Test-time critic sampling enables iterative refinement or repair, yielding substantial gains at higher sampling budgets and strong zero-shot transfer (MBPP). Limitations include extra training complexity (critic + repair model) and broader issues inherited from code LMs (bias/toxic text, insecure code, need for human verification).

## Key Contributions
- Actor–critic RL fine-tuning for program synthesis where rewards are unit-test outcomes and dense token-level weights come from a critic trained as an error predictor (4-way: CompileError/RuntimeError/FailedTest/PassedTest).
- “Critic Sampling” inference algorithm that uses example unit tests to (i) refine passing solutions via critic-selected prefix seeds and regeneration, and (ii) repair failing solutions using critic-selected candidates plus compiler error traces.
- Improved CodeT5-large (770M) foundation model via larger Python pretraining corpus (GCPY 10.5B tokens) and added NTP pretraining; achieves SOTA on APPS and MBPP (zero-shot 63.0 pass@80).

## Potential Relevance
CodeRL is a concrete recipe for injecting *execution-based supervision* into code generation without requiring differentiable execution: train a critic on test outcomes, then use critic-weighted policy gradients plus a variance-reducing baseline. The inference-time repair/refine loop (seed selection by critic + regeneration; compiler-trace-conditioned repair model) is especially relevant for hypotheses about *test-time compute* and *self-correction* in LMs. The paper’s ablations (absolute vs relative rewards; token-level critic vs heuristics; CS components) provide useful knobs for designing new RL/verification hybrids and for diagnosing where gains come from (training signal vs search).