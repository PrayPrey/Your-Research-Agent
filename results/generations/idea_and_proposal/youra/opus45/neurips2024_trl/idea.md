# Research Idea

## Title
Structural Adapter for Table-Aware Prompting: Reducing In-Context Example Requirements for LLM Table Reasoning

## Motivation
Large Language Models struggle with table understanding tasks, requiring numerous in-context examples to achieve reasonable accuracy. While tables dominate real-world data landscapes, LLMs lack explicit mechanisms to comprehend 2D positional relationships inherent in tabular structures. Existing approaches either fine-tune entire models (expensive) or rely on extensive prompting (inefficient). Recent work shows schema scaffolding can dramatically improve LLM reasoning (up to 36% gains), yet no method systematically bridges specialized table encoders with frozen LLMs to reduce example requirements.

## Main Idea
We propose SATA-SP (Structural Adapter for Table-Aware Structural Prompting), which injects learned structural prompts into frozen LLMs to improve table reasoning efficiency. The core mechanism operates in three steps: (1) TAPAS-style embeddings capture row/column positional relationships, (2) a lightweight projection network translates these embeddings into soft prompt tokens, and (3) prepended structural prompts provide explicit positional scaffolding to the LLM. We hypothesize this reduces the "cognitive load" on LLMs for structural reasoning, enabling comparable accuracy with 50% fewer in-context examples. Experiments on WikiTableQuestions, TabFact, and FeTaQA will measure in-context efficiency gains and zero-shot transfer. Success would establish a parameter-efficient paradigm for enhancing LLM table understanding without costly fine-tuning, with broad applications in data analysis and question answering.