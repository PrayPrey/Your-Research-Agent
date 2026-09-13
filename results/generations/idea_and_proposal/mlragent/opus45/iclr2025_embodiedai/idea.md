# Title: Hierarchical Spatial Memory Networks for Long-Horizon Navigation of LLM Agents in Open City Environments

## Motivation
Current LLM agents struggle with long-horizon navigation in large-scale urban environments because they lack persistent, structured spatial memory. Unlike humans who build cognitive maps at multiple abstraction levels (landmarks, routes, regions), LLM agents typically process spatial information in a flat, context-limited manner. This leads to poor performance in tasks requiring backtracking, shortcut discovery, or reasoning about distant locations. Developing human-like hierarchical spatial memory is crucial for enabling robust embodied intelligence in open city environments.

## Main Idea
We propose a **Hierarchical Spatial Memory Network (HSMN)** that augments LLM agents with a multi-level spatial memory structure inspired by human cognitive maps. The architecture consists of three layers: (1) a **landmark layer** storing salient visual-semantic features of key locations, (2) a **route layer** encoding traversable paths and their attributes (distance, accessibility, scene transitions), and (3) a **region layer** capturing abstract neighborhood-level representations and inter-region connectivity.

The methodology involves training a graph neural network to dynamically update this hierarchy during exploration, with the LLM querying relevant memory levels based on task requirements. We will evaluate HSMN on city-scale navigation benchmarks, measuring success rate, path efficiency, and generalization to unseen areas.

**Expected outcomes**: Significant improvements in long-horizon navigation and spatial reasoning, with interpretable memory structures enabling better human-agent collaboration in urban applications like delivery and emergency response.