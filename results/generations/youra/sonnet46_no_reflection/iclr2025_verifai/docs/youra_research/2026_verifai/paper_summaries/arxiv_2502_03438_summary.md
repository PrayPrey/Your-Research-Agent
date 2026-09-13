---
source_paper: "arxiv_2502_03438.md"
generated_at: "2026-05-20T07:26:23.157289"
model: "gpt-4.1-mini"
summary_chars: 8451
---

# BFS-Prover: Scalable Best-First Tree Search for LLM-based Automatic Theorem Proving

## Key Metadata
- **Authors:** Ran Xin et al.
- **Year:** 2025 (arXiv 2502.03438)
- **Venue:** arXiv (preprint, formal ATP domain)
- **Core Contribution:** Introduces BFS-Prover, a scalable expert iteration framework that uses a length-normalized Best-First Search combined with Direct Preference Optimization and data filtering to achieve state-of-the-art results on formal theorem proving with large language models (LLMs).

## Section Summaries

### Abstract
Recent advancements in large language models (LLMs) have spurred growing interest in automatic theorem proving using Lean4, where effective tree search methods are crucial for navigating the underlying large proof search spaces. While the existing approaches primarily rely on value functions and/or Monte Carlo Tree Search (MCTS), the potential of simpler methods like Best-First Tree Search (BFS) remains underexplored. In this paper, we investigate whether BFS can achieve competitive performance in large-scale theorem proving tasks. We present BFS-Prover, a scalable expert iteration framework, featuring three key innovations. First, we implement strategic data filtering at each expert iteration round, excluding problems solvable via beam search node expansion to focus on harder cases. Second, we improve the sample efficiency of BFS through Direct Preference Optimization (DPO) applied to state-tactic pairs automatically annotated with compiler error feedback, refining the LLM’s policy to prioritize productive expansions. Third, we employ length normalization in BFS to encourage exploration of deeper proof paths. BFS-Prover achieves a state-of-the-art score of 72.95% on the MiniF2F test set and therefore challenges the perceived necessity of complex tree search methods, demonstrating that BFS can achieve competitive performance when properly scaled. To facilitate further research and development in this area, we have open-sourced our model.

### Introduction & Motivation
Automatic theorem proving (ATP) with formal languages like Lean4 is a challenging benchmark for reasoning in LLMs due to strict syntax, semantics, and a vast action (tactic) space. Existing ATP approaches commonly use Monte Carlo Tree Search (MCTS) with value functions, but ATP differs from classical games due to ambiguous terminal conditions, enormous branching factors, and sparse feedback, complicating MCTS application. Best-First Search (BFS), a simpler method prioritizing nodes by cumulative log probabilities, is dismissed in prior work for lacking exploration and biasing against deep proofs. This paper challenges this view by scaling BFS with new techniques, demonstrating BFS can match or exceed more complex methods in large-scale ATP.

### Methodology

**Core algorithm: Length-Normalized Best-First Search (BFS) with expert iteration**

1. **Best-First Tree Search (BFS):**  
   - Maintains a priority queue of proof states (nodes).  
   - Node scoring heuristic normalizes cumulative log probabilities by path length:  
     \[
     \text{score}(s_L) = \frac{\sum_{t=0}^{L-1} \log p(a_t | s_t)}{L^\alpha}
     \]
     where:  
     - \( s_t \): proof state at step \(t\)  
     - \( a_t \): tactic applied at step \(t\)  
     - \( p(a_t | s_t) \): predicted probability by policy LLM  
     - \( L \): path length  
     - \( \alpha \in [0,1] \): length normalization hyperparameter, tuning exploration vs. exploitation  
   
   This normalization mitigates BFS's inherent bias against longer, deeper proof paths, encouraging exploration of complex proofs.

2. **Expert Iteration Framework:**  
   Iteratively improves policy LLM via cycles:  
   - **Beam Search Filtering:**  
     - Removes problems solvable by BFS with beam search node expansions from the training corpus, focusing data accumulation on harder problems.  
   - **Data Collection via BFS Sampling:**  
     - Performs BFS using temperature-based sampling to collect state-tactic pairs along successful proof paths and records tactics causing Lean compiler errors as negative examples.  
   - **Supervised Fine-Tuning (SFT):**  
     - Trains the policy LLM on accumulated state-tactic pairs for 3 epochs using cosine learning rate decay (from \(2 \times 10^{-5}\) to \(1 \times 10^{-6}\)) with global batch size 128, on A100 GPUs.  
   - **Direct Preference Optimization (DPO):**  
     - Leverages negative examples from Lean4 compiler feedback to form preference pairs \((a_w, a_l)\), where \(a_w\) is a positive (proof path) tactic and \(a_l\) is a negative (error-causing) tactic at the same state.  
     - DPO loss:
       \[
       L_{\text{DPO}}(\theta) = -\mathbb{E}_{(s,a_w,a_l)} \left[ \log \sigma \left( \beta (r_\theta(s,a_w) - r_\theta(s,a_l)) \right) \right]
       \]
       where  
       \[
       r_\theta(s,a) = \log p_\theta(a|s) - \log p_{\text{ref}}(a|s)
       \]
       \(\sigma(\cdot)\) is sigmoid, \(\beta=10\) is KL regularization controlling preference sharpness, and \(p_{\text{ref}}\) is a reference model.  
     - DPO is realized with a 1-epoch training run, smaller batch size (16), and serves as a sample-efficient alternative to SFT when data is scarce.  

3. **LeanDojo Environment:**  
   - Provides a Python gym-like interface connecting the policy LLM with Lean4.  
   - Executes tactics and returns execution states or error messages, essential for collecting interaction data used in DPO.

4. **Distributed Implementation:**  
   - Ray framework manages distribution over multiple machines (each with 8 A100 GPUs, 128 CPUs).  
   - Multiple policy LLM instances (7B parameter Qwen2.5-Math-7B finetuned) and prover instances run concurrently.  
   - Prover instances perform BFS in parallel, asynchronously querying the shared policy LLM pool and LeanDojo environments.  
   - This design achieves near-linear scaling without cross-machine communication during search.

5. **Hyperparameters:**  
   - Length normalization \( \alpha \): set to 0.0 during early expert iteration; varied in later experiments among {0.0, 0.5, 1.0}.  
   - Beam search width during filtering: 32.  
   - BFS sampling temperature: 1.0-1.1 with nucleus sampling parameter 1.0.  
   - Expansion width during sampling: 2, 4, or 8.  
   - SFT training: 3 epochs, learning rate decay from \(2 \times 10^{-5}\) to \(1 \times 10^{-6}\).  
   - DPO training: 1 epoch, decay from \(5 \times 10^{-6}\) to \(5 \times 10^{-7}\), KL \(\beta=10\).

6. **Novel Components Compared to Prior Work:**  
   - Demonstrates for the first time that BFS, combined with length normalization and policy refinement via DPO from compiler feedback, can match or exceed MCTS-based ATP results.  
   - Strategic expert iteration filtering to focus on harder problems.  
   - Using negative feedback from compiler errors explicitly in policy training (DPO).  
   - Scalable distributed implementation tailored to large-scale ATP.

### Experiments & Results

**Datasets & Training Data:**  
- Base model: Qwen2.5-Math-7B, finetuned from Mathlib extracted proofs for cold start.  
- Training corpus: roughly 900K formal mathematical statements without proofs, derived from numinaMath-CoT, Mathlib, Lean-Github, and Lean-Workbook datasets.  
- Expert iteration conducted over 10 rounds, accumulating state-tactic pairs and refining the policy model.

**Evaluation Benchmark:**  
- MiniF2F benchmark: widely used formal mathematics competition problems dataset.  
- Test achieves 72.95% success rate (accumulative over multiple BFS configurations), exceeding previous state-of-the-art provers.

**Baselines Compared:**  
| Prover System                      | Critic + MCTS | Tactic Budget (Calls) | MiniF2F-Test Accuracy |
|----------------------------------|---------------|----------------------|-----------------------|
| DeepSeek-Prover-V1.5 (2024b)     | No            | \(32 \times 16 \times 400\) | 63.5%                 |
| InternLM2.5-StepProver (2024a)   | Yes           | \(256 \times 32 \times 600\) | 65.9%                 |
| HunyuanProver (2024b)             | Yes           | \(600 \times 8 \times 400\)  | 68.4%                 |
| **BFS-Prover (this work)**        | No            | \(2048 \times 2 \times 600\) | **70.83% ± 0.89%**    |
| BFS-Prover accumulative over configs | No         | -                    | **72.95%**            |

- BFS-Prover obtains these results without critic models or MCTS.

**Ablations