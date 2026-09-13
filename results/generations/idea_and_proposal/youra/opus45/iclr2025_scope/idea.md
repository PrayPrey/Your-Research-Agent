## Title
DT-CaPEFT: Dual-Timescale Context-Aware Parameter-Efficient Fine-Tuning for Continual Learning

## Motivation
Continual learning with foundation models faces a fundamental tension: complex inputs require high-capacity adapters for accuracy, while simple inputs waste parameters with over-provisioned representations. Current PEFT methods use fixed-rank adapters regardless of input complexity, leading to inefficiency. This research addresses the gap between adaptive capacity allocation and continual learning, inspired by how biological memory systems (hippocampus-neocortex) consolidate knowledge at different timescales based on information complexity.

## Main Idea
We propose DT-CaPEFT, which dynamically routes between low-rank (r=4) and high-rank (r=32) adapters based on input complexity measured via attention entropy. The core mechanism operates in three steps: (1) compute attention entropy as a complexity signal, (2) soft-gate between fast (low-rank) and slow (high-rank) adapters proportionally, and (3) consolidate knowledge from slow to fast adapters via exponential moving average updates.

**Key hypothesis:** Context complexity determines optimal adapter capacity—simple inputs achieve 95%+ performance using only 12.5% of parameters, while complex inputs benefit from full capacity.

**Methodology:** Ablation studies on SCROLLS and LongBench comparing DT-CaPEFT against PEARL and C-LoRA baselines, measuring accuracy, forgetting rate, and parameter efficiency across complexity-stratified inputs.

**Expected outcomes:** 40-60% parameter reduction on simple contexts while maintaining continual learning performance, with <5% computational overhead.