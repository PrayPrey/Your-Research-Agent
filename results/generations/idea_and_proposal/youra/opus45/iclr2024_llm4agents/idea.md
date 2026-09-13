## Title
Parameter-Free Spreading Activation Memory Consolidation for Long-Running LLM Agents

## Motivation
Long-running LLM agents (100+ conversation turns) suffer from catastrophic forgetting and poor multi-hop recall as episodic memories accumulate. Current solutions either rely on static RAG retrieval (missing semantic connections) or require costly parameter fine-tuning during "sleep" phases. A critical gap exists: can we achieve robust memory consolidation through pure graph operations, preserving base LLM capabilities while improving long-term recall?

## Main Idea
We propose Spreading Activation Memory Consolidation (SAMC), a parameter-free mechanism inspired by cognitive sleep consolidation. During offline phases, SAMC operates on episodic-semantic memory graphs through: (1) **NREM-like tight replay**—propagating activation from recent high-importance nodes, strengthening co-activated edges, and pruning weak connections via lateral inhibition; (2) **REM-like free exploration**—allowing activation to spread freely, discovering distant semantic connections and extracting gist patterns into new semantic nodes.

The core hypothesis: SAMC will improve multi-hop recall accuracy by ≥15% and reduce catastrophic forgetting by ≥20% compared to static RAG, without any gradient computation. We will validate through controlled experiments on LoCoMo benchmarks, comparing against MemGPT and SYNAPSE baselines across conversation lengths (100-500 turns).

This approach uniquely enables async CPU-based consolidation during idle time, preserving LLM weights while providing interpretable, inspectable memory operations—critical for practical deployment of persistent conversational agents.