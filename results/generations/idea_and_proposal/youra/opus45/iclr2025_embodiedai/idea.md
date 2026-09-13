## Title
StigmaLLM: Stigmergic Coordination via Hierarchical Semantic Pheromone Fields for Multi-Agent Urban Navigation

## Motivation
Current LLM-based embodied agents struggle with scalable coordination in open urban environments. Existing approaches rely on direct peer-to-peer communication, which suffers from O(N²) message complexity and catastrophic failure under communication disruptions—critical limitations for real-world deployment in search-and-rescue or multi-robot delivery. Biological swarms solve similar coordination challenges through stigmergy: indirect communication via environmental markers. This research bridges swarm intelligence principles with LLM reasoning capabilities to enable robust, scalable multi-agent coordination.

## Main Idea
We propose Hierarchical Semantic Pheromone Fields (H-SPF), where LLM agents coordinate indirectly by reading/writing typed semantic pheromones (EXPLORE, OBSTACLE, CROWD, GOAL) to shared octree-based spatial memory. The causal mechanism operates through four steps: agents write pheromones upon local observations → octree hierarchically propagates information → nearby agents query local pheromone gradients with O(1) complexity → pheromone-augmented prompts guide LLM navigation decisions.

Key predictions: (1) per-agent communication remains O(1) as agents scale from 2 to 16, (2) coordination efficiency exceeds direct-communication baselines (CAMON, SAMALM) by >15%, and (3) task completion degrades <20% under 50% communication failure versus >50% for baselines. Experiments on Multi-Agent CityEQA will validate scalability, efficiency, and resilience, establishing a new paradigm for decentralized LLM coordination in urban environments.