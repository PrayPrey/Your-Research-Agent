# Research Idea

## Title
CompDAG: Diagnosing Compositional Generalization via IRT-Calibrated DAG Benchmarks with Depth-Decay Analysis

## Motivation
Distinguishing genuine compositional generalization from sophisticated pattern matching in language models remains a critical challenge for System-2 reasoning evaluation. Existing benchmarks suffer from contamination and fail to systematically isolate compositional complexity. Current evaluations cannot reliably determine whether models recursively apply learned primitives (true composition) or retrieve memorized patterns that degrade with complexity. This gap undermines our ability to assess AI safety and develop architectures with genuine reasoning capabilities.

## Main Idea
We propose modeling compositional tasks as parameterized Directed Acyclic Graphs (DAGs) with three controllable dimensions: Composition Depth (D), Working Memory Load (W), and Interference Level (I), calibrated using Item Response Theory. The core hypothesis: models with genuine compositional generalization exhibit **flat/sublinear accuracy decay** with increasing depth, while pattern-matching models show **exponential decay**—because true composition applies primitives recursively (O(1) per step), whereas pattern matching searches an exponentially growing space.

The methodology involves: (1) procedurally generating semantic parsing tasks from fixed grammar primitives with varying DAG structures, (2) calibrating difficulty via hierarchical IRT (target r>0.8), and (3) analyzing decay curves across model architectures. Success criteria include statistically significant decay slope differences (>0.05) between model types.

This framework provides contamination-resistant evaluation and a diagnostic tool for identifying which models possess genuine System-2 compositional capabilities versus surface-level pattern matching.