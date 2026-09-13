# Research Idea

## Title
Two-Phase Meta-Learned Expert Primitives for Compositional In-Context Reinforcement Learning

## Motivation
Despite breakthroughs in reinforcement learning, applying RL to novel problems remains brittle and heavily engineered. In-context RL (ICRL) methods like Algorithm Distillation show promise but struggle with cross-domain generalization beyond training distributions. Recent work (T2MIR) combines Mixture-of-Experts with ICRL using end-to-end training, but lacks explicit optimization for compositional skill primitives. This gap limits generalization to truly novel task categories—a critical barrier for practical AutoRL systems.

## Main Idea
We hypothesize that **two-phase training**—first meta-learning specialized expert policy modules with diversity regularization, then training a transformer-based in-context router—enables superior compositional generalization compared to end-to-end approaches. The key mechanism: explicit meta-training produces diverse, specialized primitives that the router can flexibly compose via soft attention for novel tasks, whereas end-to-end training conflates primitive learning with routing optimization.

**Methodology:** On Meta-World ML45, we train K=8-32 small transformer experts with diversity loss, then freeze experts and train the router on in-context trajectories. We compare against AD, DPT, and T2MIR baselines.

**Predictions:** >15% success rate improvement on held-out task categories versus monolithic ICRL; >5% versus T2MIR; expert utilization entropy >1.5 nats confirming specialization.

**Impact:** Establishes principled compositional structure for AutoRL generalization.