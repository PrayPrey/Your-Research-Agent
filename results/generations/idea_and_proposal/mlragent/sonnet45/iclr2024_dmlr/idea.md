## Title
Adaptive Quality Filtering: Learning Dynamic Data Selection Policies for Foundation Model Training

## Motivation
Foundation models are trained on massive datasets scraped from the web, yet most approaches apply static quality filters (e.g., fixed perplexity thresholds, rule-based heuristics). This is inefficient because: (1) quality signals evolve as models learn—easy high-quality samples become less informative over time, (2) different training stages benefit from different data characteristics, and (3) static filters may inadvertently remove valuable diverse examples. Current methods waste computation on uninformative data or prematurely discard useful samples.

## Main Idea
We propose a meta-learning framework that trains a lightweight **data selection policy network** alongside the foundation model. The policy network learns to predict sample utility scores based on: (1) current model state (training loss, layer activations), (2) sample features (perplexity, domain tags, syntactic complexity), and (3) training dynamics (loss trajectories on validation sets).

**Methodology**: Use reinforcement learning where the reward signal is validation performance improvement per compute unit. The policy network periodically updates its selection criteria, creating a curriculum that adapts from broad diverse data early in training to targeted high-quality data later.

**Expected Outcomes**: 20-30% reduction in training compute while maintaining or improving model quality, demonstrated through experiments on language and multimodal foundation models. This enables more sustainable and efficient large-scale training while automatically discovering domain-specific quality signals.