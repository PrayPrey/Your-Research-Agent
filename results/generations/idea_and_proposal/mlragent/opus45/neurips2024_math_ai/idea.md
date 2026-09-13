# Title: Adaptive Difficulty Calibration for Mathematical Reasoning Benchmarks via Student-Teacher LLM Dynamics

## Motivation
Current mathematical reasoning benchmarks suffer from two critical issues: (1) static difficulty levels that become quickly saturated as LLMs improve, and (2) contamination concerns where test problems may appear in training data. This makes it increasingly difficult to accurately measure genuine mathematical reasoning progress versus memorization. We need dynamic, self-evolving benchmarks that can reliably distinguish true reasoning capabilities from pattern matching while automatically calibrating to the frontier of model abilities.

## Main Idea
I propose a **student-teacher framework** for continuously generating and calibrating mathematical reasoning benchmarks. A "teacher" LLM generates novel problems by composing atomic mathematical concepts in unprecedented combinations, while a panel of "student" LLMs of varying capabilities attempts solutions. Problems are scored and retained based on their **discriminative power**—the ability to separate models by reasoning depth rather than knowledge recall.

The methodology involves:
1. Concept graph construction from mathematical curricula
2. Procedural problem generation through novel concept compositions
3. Multi-model difficulty calibration using Item Response Theory
4. Automated verification of solutions via symbolic solvers

Expected outcomes include a living benchmark that resists saturation and contamination, plus insights into which mathematical concept combinations reveal true reasoning gaps. This addresses the "measuring mathematical reasoning" challenge while providing a practical tool for tracking genuine progress in the field.