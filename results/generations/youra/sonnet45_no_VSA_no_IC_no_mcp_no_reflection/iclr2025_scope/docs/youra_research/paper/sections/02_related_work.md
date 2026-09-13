# Related Work

Our work bridges three research areas: parameter-efficient fine-tuning, sub-quadratic architectures, and transfer learning. We position our contribution at their intersection, revealing architectural constraints that prior work in each area has not systematically explored.

## Parameter-Efficient Fine-Tuning

Low-rank adaptation (LoRA) [Hu et al., 2021] introduced a principled approach to fine-tuning large models by injecting low-rank weight updates into linear layers, reducing trainable parameters by orders of magnitude while matching full fine-tuning performance. Subsequent work explored alternative PEFT strategies: prefix tuning [Li and Liang, 2021] prepends learnable tokens to input sequences, prompt tuning [Lester et al., 2021] optimizes continuous prompts, and adapters [Houlsby et al., 2019] insert lightweight bottleneck layers. These methods share a common assumption: the base model architecture already possesses the capabilities needed for the target task.

Critically, all established PEFT research focuses exclusively on transformer architectures—BERT [Devlin et al., 2019], GPT-2 [Radford et al., 2019], T5 [Raffel et al., 2020], and their variants. Transformers' bidirectional self-attention enables flexible information flow suitable for diverse tasks. This architectural versatility has allowed PEFT literature to treat the base model as a black box, focusing on *which parameters to adapt* rather than *whether adaptation is possible*. Our work challenges this assumption by testing PEFT transfer to architecturally distinct model families.

## State-Space Models and Sub-Quadratic Architectures

State-space models emerged as efficient alternatives to transformers, replacing quadratic attention with linear-time recurrent dynamics. Structured state-space models (S4) [Gu et al., 2022] introduced parameterization techniques enabling stable training of deep SSM layers, achieving competitive performance on long-range benchmarks. Mamba [Gu and Dao, 2023] extended S4 with selective state-space mechanisms and hardware-aware implementations, demonstrating strong results on language modeling and generation tasks.

However, SSM research has primarily evaluated generative capabilities—language modeling perplexity, long-context understanding, and sequence generation. Classification tasks, especially those requiring bidirectional reasoning, remain underexplored. Mamba's design inherits causal constraints from language modeling: the model processes sequences left-to-right, with each token's representation depending only on preceding context. This architectural choice optimizes generation but may impose fundamental limitations on tasks requiring symmetric comparison.

Other sub-quadratic architectures—linear attention [Katharopoulos et al., 2020], RWKV [Peng et al., 2023], and Hyena [Poli et al., 2023]—share similar motivations but differ in implementation. Our focus on Mamba as a representative causal SSM provides a testbed for understanding how architectural constraints affect PEFT applicability.

## Transfer Learning and Architectural Compatibility

Classical transfer learning research [Pan and Yang, 2010; Yosinski et al., 2014] established that pretrained representations accelerate downstream task learning. Recent work has explored domain shift [Ganin et al., 2016], task similarity [Zamir et al., 2018], and few-shot adaptation [Brown et al., 2020]. Yet these studies assume architectural compatibility: the source and target tasks must be solvable by the same model architecture.

Zero-shot evaluation has been used primarily to assess pretrained model quality [Radford et al., 2019] rather than as an architectural compatibility test. Our work reframes zero-shot performance as a critical gating mechanism: below-random accuracy signals architectural mismatch that PEFT cannot overcome. This perspective shifts zero-shot evaluation from a benchmark metric to a prerequisite validation step.

## Positioning Our Contribution

Prior PEFT research demonstrates *how* to efficiently adapt transformers but does not address *when* adaptation is possible across architectures. SSM research validates efficiency but has not systematically tested architectural limitations on classification tasks. Transfer learning assumes compatibility but lacks principled methods to validate it a priori.

We contribute the first systematic evaluation of PEFT transfer across architecture families, revealing that causal SSMs fail bidirectional tasks at zero-shot evaluation—a failure pattern that LoRA fine-tuning cannot fix. Our task-architecture compatibility framework establishes architectural validation as a prerequisite for PEFT, preventing wasted compute on structurally impossible experiments. As the field explores diverse efficient architectures, understanding these constraints becomes essential for practitioners deploying PEFT methods beyond transformers.
