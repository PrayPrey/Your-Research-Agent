# Research Idea

## Title
Curiosity-Driven Skill Chaining: Learning Compositional Skills through Intrinsic Motivation over Skill Graphs

## Motivation
Current intrinsically motivated agents excel at discovering individual skills but struggle to compose them into complex, hierarchical behaviors that generalize across domains. Humans naturally chain simple skills (grasping, lifting, placing) into sophisticated sequences (cooking, building), guided by curiosity about novel skill combinations. Existing approaches either learn flat skill libraries or rely on predefined hierarchies, limiting open-ended learning. We need mechanisms that autonomously discover *how* skills can be composed and *which* compositions are worth exploring.

## Main Idea
We propose a framework where agents maintain a dynamic **skill graph** representing learned skills as nodes and discovered compositional relationships as edges. The key innovation is a **compositional curiosity** signal that rewards the agent for discovering novel, successful skill chains rather than just individual skills.

The methodology involves: (1) A skill embedding space where proximity indicates composability potential; (2) An intrinsic reward combining prediction error on composition outcomes with novelty of the resulting behavior; (3) A graph neural network that predicts promising unexplored compositions based on structural patterns in the skill graph.

Expected outcomes include agents that autonomously discover hierarchical skill structures, generalize to new tasks by recombining known skills, and exhibit curriculum-like progression from simple to complex behaviors. This addresses the critical gap between skill discovery and flexible, lifelong skill integration in open-ended environments.