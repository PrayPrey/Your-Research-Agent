# Title: Prompt Fingerprinting for LLM Copyright Protection and Unauthorized Usage Detection

## Motivation:
As LLMs become valuable commercial assets, protecting proprietary models from unauthorized usage is increasingly critical. Current watermarking techniques focus on embedding signals in model weights or outputs, but they can be circumvented through fine-tuning or output paraphrasing. A significant gap exists in detecting whether a third-party service is illegally using a protected LLM behind their API. This research addresses the urgent need for robust copyright protection mechanisms that can verify model ownership even when direct model access is unavailable.

## Main Idea:
We propose **Prompt Fingerprinting**, a novel technique that embeds unique, verifiable behavioral signatures into LLMs during training. The key insight is to train models to produce specific, semantically-neutral trigger responses when given carefully crafted "fingerprint prompts"—rare, non-natural input patterns that won't occur in normal usage.

Our methodology involves: (1) designing cryptographically-secured fingerprint prompt-response pairs that are statistically improbable to occur naturally; (2) integrating these during instruction tuning with minimal impact on model utility; (3) developing a verification protocol to query suspected infringing services.

We expect this approach to be robust against fine-tuning, quantization, and prompt manipulation while maintaining model performance. The potential impact includes enabling model owners to legally verify unauthorized commercial usage, establishing forensic evidence for IP litigation, and creating a new paradigm for LLM ownership verification in black-box settings.