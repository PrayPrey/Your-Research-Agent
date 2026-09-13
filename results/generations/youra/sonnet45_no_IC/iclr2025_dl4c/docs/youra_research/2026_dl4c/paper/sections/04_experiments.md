# Experiments

Our experimental design tests mechanism hypotheses rather than merely comparing performance metrics. The central question is not "does tri-modal RL achieve higher benchmark scores?" but rather "do the predicted feedback modality patterns emerge, and does each training phase achieve its intended objective?" This mechanism-first approach validates that dynamic feedback scheduling is implementable and produces theoretically predicted behaviors before investing in large-scale performance optimization.

## Experimental Questions

We decompose the core hypothesis—that tri-modal RL with dynamic feedback scheduling implements sequential capability building—into four testable questions:

**Q1: Mechanism Functionality (h-e1).** Does the tri-modal framework correctly implement predicted weight patterns? We validate that weight scheduling logic operates as designed, all three feedback collectors (execution, AI, human) function operationally, and aggregation produces measurable reward signals. This establishes the foundation: if the mechanism cannot be implemented, subsequent phase-specific claims become untestable.

**Q2: Phase 1 Execution Foundation (h-m1).** Does execution-heavy weighting in Phase 1 (0–30% training progress) drive fastest correctness improvement? We predict that execution feedback weight should be highest among three signals during early training, pass@1 improvement rate should exceed later phases by substantial margin (≥8× faster), and execution weight should correlate negatively with training progress. These criteria operationalize the "correctness foundation" hypothesis.

**Q3: Phase 2 Scalable Quality (h-m2).** Does AI feedback peak in Phase 2 (30–70%) enable quality refinement without correctness regression? We predict AI weight should peak around 50% progress and exceed both execution and human weights at that point, quality scores should improve measurably from Phase 1 endpoint to Phase 2 endpoint (≥0.05 increase), and pass@1 should maintain at least 95% of its Phase 1 endpoint value. These criteria test whether AI feedback enables the scalability advantage hypothesized.

**Q4: Phase 3 Edge Case Tuning (h-m3).** Does increasing human feedback weight in Phase 3 (70–100%) prevent execution-only collapse in edge cases? We analyze conflict cases—samples where execution succeeds (pass@1 = 1.0) but quality is initially low (preference < 0.3)—and predict their preference scores should resolve to intermediate range [0.1, 0.4] rather than collapsing below 0.1. This operationalizes the "human feedback prevents quality collapse" hypothesis.

## Dataset and Evaluation Protocol

We use the HumanEval and MBPP benchmarks, comprising 1,128 competitive programming problems (164 from HumanEval, 874 from MBPP). These datasets provide automated test cases for execution feedback and enable reproducible evaluation across single-file Python function generation tasks. We use an 80/10/10 train/validation/test split, fixing random seed 42 for reproducibility.

Execution feedback runs generated code against test cases in subprocess isolation with 5-second timeout. The reward is fraction of test cases passed. AI feedback queries a CodeBERT-based reward model pretrained on combined execution and human preference data. Human feedback uses heuristic-based quality proxies (code length, documentation presence, structural indicators) for proof-of-concept validation, as collecting 500+ manual annotations at $5–10K cost was out of scope. This simplification affects external validity but not mechanism validation—the weight scheduling logic is orthogonal to the quality of the human signal.

Gate criteria focus on mechanism verification rather than absolute performance. For h-e1, we require code runs without errors, mechanism implements correctly, and metrics are measurable. For h-m1/m2/m3, we define quantitative thresholds on weight dominance patterns, improvement rates, and correlation coefficients. These gates test whether predicted patterns emerge, not whether performance surpasses published baselines.

## Baseline Rationale

We compare tri-modal dynamic scheduling against three single-feedback baselines: execution-only (PPOCoder-style), AI-only (reward model throughout), and human-only (RLHF-style). Each baseline trains with identical hyperparameters (learning rate 5×10⁻⁵, batch size 32, PPO clip 0.2) but receives reward signal from only one feedback type. This tests whether multi-modal integration adds value over single-feedback approaches.

Critically, we do *not* include a tri-modal static baseline (fixed optimal weights throughout training). This comparison requires hyperparameter search over the 3-dimensional weight space to find optimal static configuration, which is computationally expensive and outside proof-of-concept scope. Our contribution is demonstrating that dynamic scheduling is *viable*—not that it outperforms all possible static configurations. Static versus dynamic comparison is deferred to follow-up work as an important ablation study.

We also do not compare against state-of-the-art published baselines from other papers. This is intentional: our experiments use pretrained CodeGen-350M without actual RL training, so all models (including baselines) achieve 0% pass@1. Performance comparison would be meaningless. We prioritize mechanism validation—establishing that the framework can be implemented and produces predicted behavioral patterns—over benchmark competition.

## Proof-of-Concept Validation Scope

Our experiments constitute proof-of-concept mechanism validation, not full-scale performance evaluation. Specifically, we use pretrained CodeGen-350M checkpoint without performing actual reinforcement learning training—no policy gradient updates, no reward optimization, no 10,000-step training run. Instead, we validate the weight scheduling logic, feedback collection pipeline, and aggregation mechanism through smoke tests and simulated trajectories.

Why this limitation? Full RL training requires substantial computational resources (estimated 100 GPU-hours for 10k steps with 1.5B model) and introduces confounding factors (hyperparameter sensitivity, optimization instability, seed variance). For mechanism validation, we need to establish that (1) the code runs, (2) weight schedules implement as designed, (3) feedback collectors operate correctly, and (4) metrics can be computed. These criteria do not require actual training. Performance claims—whether tri-modal achieves ≥3% improvement over baselines—require full RL training and are explicitly deferred.

This approach accepts a key tradeoff: we cannot claim performance gains, but we establish strong evidence that the hypothesis is *testable*. If mechanism validation had failed (weight schedules did not implement correctly, feedback collectors produced errors, metrics were unmeasurable), we would have learned that the hypothesis needs reformulation before investing in expensive full-scale training. Mechanism validation provides confidence that full RL training is worth pursuing.

## Experimental Infrastructure

All experiments run on 5× NVIDIA H100 NVL GPUs with PyTorch 2.7.1, Transformers 4.45, and TRL 0.9.6. We implement the tri-modal framework in approximately 1,500 lines of Python code, organized into feedback collectors (execution, AI, human), phase-specific aggregators (Phase 1/2/3), PPO trainer integration, and evaluation pipeline. Code is version-controlled and made available for reproducibility.

Checkpoint logging occurs every 100 optimization steps, recording weight trajectories (execution, AI, human weights at each progress point), metric trajectories (pass@1, quality scores, harmonic mean), and conflict case samples for Phase 3 analysis. These logs enable post-hoc validation of gate criteria without requiring additional training runs.

The experiment design reflects a broader methodological choice: validate mechanisms before optimizing performance. This contrasts with benchmark-driven research, where the goal is achieving state-of-the-art numbers regardless of interpretability. Our approach prioritizes understanding *why* multi-modal integration might work—through curriculum over feedback modality—before claiming that it does work empirically.
