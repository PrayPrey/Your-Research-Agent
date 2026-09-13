# 2. Related Work

## 2.1 RLHF Evaluation Methods

Reinforcement Learning from Human Feedback (RLHF) has become the dominant paradigm for aligning language models to human preferences. InstructGPT (Ouyang et al., 2022) introduced the standard three-stage pipeline: supervised fine-tuning (SFT), reward model training from pairwise comparisons, and policy optimization via PPO. Evaluation focused on preference win rates: InstructGPT achieved 85% preference agreement vs GPT-3 base model on human evaluations. Constitutional AI (Bai et al., 2022) extended this with AI feedback for harmlessness, reporting improved safety scores while maintaining helpfulness. Both methods treat **preference convergence as success** — higher win rates indicate better alignment.

However, these benchmarks measure only **unidirectional alignment** (AI→human): does the model produce outputs humans prefer? They do not measure **bidirectional alignment** (human→AI): do humans preserve critical evaluation capacity when exposed to aligned models? High preference agreement could indicate quality improvement (users genuinely prefer better responses) or homogenization (users habituate to model style and stop critically evaluating). Existing metrics cannot distinguish these scenarios.

**WebGPT** (Nakano et al., 2021) and **OpenAI Summarization** (Stiennon et al., 2020) provide relevant precedents. OpenAI Summarization collected multi-annotator ratings on the same summary candidates, enabling variance analysis. However, their published metrics still focused on mean preference scores, not entropy or diversity measures. This suggests the data structure for diversity measurement exists in some datasets (multi-annotator fixed responses) but has not been leveraged for bidirectional alignment evaluation.

## 2.2 Bidirectional Alignment and Human Agency

Human-AI interaction research emphasizes user agency and empowerment (Amershi et al., 2019). The "Guidelines for Human-AI Interaction" framework includes principles like "support efficient correction" and "encourage granular feedback" — both requiring that users maintain critical evaluation of AI outputs. However, these guidelines rely on **self-reported measures** (user surveys, perceived control) or **interaction patterns** (override rates, feedback frequency). Our entropy approach provides a **behavioral proxy** computable from existing preference data without new human evaluation.

Reward hacking literature (Skalse et al., 2022) addresses over-optimization on proxy metrics where models exploit misspecified reward functions. Our concern is orthogonal: not model behavior pathology (exploiting rewards) but **user behavior homogenization** (converging preferences). Entropy collapse would indicate alignment succeeded at making users agree, but failed at preserving legitimate diversity on subjective tasks.

## 2.3 Information-Theoretic Diversity Measures

Shannon entropy (Shannon, 1948) H = -Σ p_i log(p_i) is the foundational measure of distribution uncertainty. Higher entropy indicates greater diversity/unpredictability; lower entropy indicates concentration/consensus. Entropy has been applied to measure diversity in ecological systems (species distribution), information retrieval (term frequency), and machine learning (policy exploration). However, its application to **human preference distributions** in alignment evaluation is novel.

Prior work on **preference diversity** in recommender systems (Nguyen et al., 2014) showed that personalized algorithms can create filter bubbles by reducing content diversity. This parallels our concern: RLHF may reduce preference diversity by training users to converge on model-preferred responses. The key difference is **measurement level**: recommender systems track individual user exposure diversity, while we propose **population-level preference entropy** as collective critical evaluation proxy.

## 2.4 Dataset Format and Annotation Cost Trade-offs

Pairwise comparison collection (Bradley-Terry models, Thurstone scaling) is standard in preference elicitation due to **annotation efficiency**: labelers compare two options (binary choice) rather than rating multiple candidates independently. Anthropic-HH (Bai et al., 2022) and WebGPT (Nakano et al., 2021) use this format: each example presents one chosen and one rejected response for a given prompt. This minimizes labeler cognitive load and enables large-scale collection (160K+ comparisons for Anthropic-HH).

However, pairwise formats create a **diversity measurement incompatibility**. To compute per-prompt preference entropy, we need **multiple annotators rating the same response candidates** — a distribution over fixed options (e.g., "40% prefer A, 35% prefer B, 25% prefer C" → H ≈ 1.05 nats). Anthropic-HH instead provides **unique response pairs per comparison** (A1 vs B1, A2 vs B2, ...), preventing aggregation into distributions.

**OpenAI Summarization** (Stiennon et al., 2020) provides a counter-example: multiple annotators rated the same summary candidates (4-5 summaries per article, 3-5 annotators per summary). This multi-annotator fixed-response format enables entropy computation but incurs higher annotation cost (N annotators × M responses per prompt vs 1 annotator per pairwise comparison). Our contribution is identifying this **format-measurement trade-off** and proposing alternatives when multi-annotator data is unavailable.

## 2.5 Positioning Our Work

We introduce **preference entropy as bidirectional alignment metric**, distinguishing our work from:
- **RLHF evaluation** (InstructGPT, Constitutional AI): Measures preference agreement (unidirectional AI→human), not diversity (bidirectional human agency preservation).
- **HCI user empowerment metrics**: Requires self-reported surveys; entropy uses behavioral data from existing benchmarks.
- **Reward hacking detection**: Focuses on model over-optimization; we address user homogenization.

Our **dataset structure taxonomy** (pairwise-unique vs multi-annotator-fixed) is a methodological contribution: first identification of data format requirements for diversity measurement in RLHF evaluation. This guides future benchmark design and explains why existing datasets cannot retrospectively measure entropy without structural changes or alternative proxies.

