# Logic Design: H-M1 (IPCR Routing)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design (no base_hypothesis code/, no existing src/)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: IPCRRouter [Complexity: 3, Budget: 2]

**Applied**: PEFT multi-adapter routing pattern (HuggingFace conceptual guide)

### API Signatures

```python
import torch
from torch import Tensor, nn
from sentence_transformers import SentenceTransformer

class IPCRRouter:
    def __init__(self, encoder: SentenceTransformer, probe: nn.Linear, adapter_names: list[str]):
        """probe: nn.Linear(384, k), loaded from H-E1 checkpoint."""
        self.encoder = encoder
        self.probe = probe
        self.adapter_names = adapter_names

    def route(self, instruction: str, top_k: int = 1) -> str | list[str]:
        """instruction -> embedding [384] -> logits [k] -> adapter name(s)."""
        ...

    def route_batch(self, instructions: list[str]) -> list[str]:
        """[B] instructions -> [B] adapter names. Batches encoder.encode."""
        ...

    @torch.no_grad()
    def _predict_logits(self, embeddings: Tensor) -> Tensor:
        """embeddings [B, 384] -> logits [B, k]"""
        return self.probe(embeddings)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| embedding | [384] | MiniLM-L6-v2 output, single instruction |
| embeddings | [B, 384] | Batched |
| logits | [B, k] | k=8 adapters |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | route() | Single-instruction routing, argmax over probe logits |
| L-1-2 | route_batch() | Batched encode + argmax for eval-scale throughput |

---

## A-2: LoRATrainer [Complexity: 3, Budget: 2]

**Applied**: PEFT LoraConfig + Trainer standard fine-tuning loop

### API Signatures

```python
from peft import LoraConfig, get_peft_model
from transformers import Trainer, TrainingArguments

class LoRATrainer:
    def __init__(self, base_model, tokenizer, lora_config: LoraConfig | None = None):
        self.base_model = base_model
        self.tokenizer = tokenizer
        self.lora_config = lora_config or LoraConfig(
            r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"],
            task_type="CAUSAL_LM",
        )

    def train_adapter(
        self, task_name: str, train_dataset, epochs: int = 3,
        batch_size: int = 8, lr: float = 2e-4,
    ) -> str:
        """Trains one LoRA on task_name subset. Returns checkpoint path."""
        ...

    def save_adapter(self, model, task_name: str, output_dir: str) -> str:
        """model.save_pretrained(output_dir/task_name). Returns saved path."""
        ...
```

### Pseudo-code (train_adapter)

```
1. peft_model = get_peft_model(base_model, self.lora_config)
2. args = TrainingArguments(output_dir=f"ckpt/{task_name}", num_train_epochs=epochs,
          per_device_train_batch_size=batch_size, learning_rate=lr, seed=42)
3. trainer = Trainer(peft_model, args, train_dataset=train_dataset, tokenizer=tokenizer)
4. trainer.train()
5. path = self.save_adapter(peft_model, task_name, args.output_dir)
6. return path
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | train_adapter() | Per-task LoRA fine-tune loop (AdamW, 3 epochs) |
| L-2-2 | save_adapter() | Checkpoint save with task_name-keyed dir |

---

## A-3: MultiAdapterModel [Complexity: 3, Budget: 2]

**Applied**: PEFT `load_adapter` / `set_adapter` / `set_adapters` (weighted ensemble, PEFT 0.8.0+)

### API Signatures

```python
from peft import PeftModel

class MultiAdapterModel:
    def __init__(self, base_model, tokenizer):
        self.model = base_model
        self.tokenizer = tokenizer
        self.adapter_names: list[str] = []

    def load_adapters(self, adapter_paths: dict[str, str]) -> None:
        """adapter_paths: {task_name: checkpoint_dir}. Loads all via PeftModel.load_adapter."""
        ...

    def set_adapter(self, adapter_name: str) -> None:
        """O(1) switch (~5ms). Delegates to self.model.set_adapter."""
        self.model.set_adapter(adapter_name)

    def set_uniform(self) -> None:
        """Equal-weight ensemble over all loaded adapters (FR-6)."""
        weights = [1.0 / len(self.adapter_names)] * len(self.adapter_names)
        self.model.set_adapters(self.adapter_names, weights=weights)

    def generate(self, instruction: str, **gen_kwargs) -> str:
        """Tokenize -> model.generate -> decode. Uses currently active adapter."""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | load_adapters() | Load k=8 named LoRAs onto base model once |
| L-3-2 | set_adapter/set_uniform/generate | Adapter switching + uniform ensemble + generate wrapper |

---

## A-4: EvaluationPipeline [Complexity: 4, Budget: 2]

**Applied**: HuggingFace `evaluate` (accuracy, rouge, exact_match) + scipy paired t-test

### API Signatures

```python
import evaluate
from scipy import stats

class EvaluationPipeline:
    def __init__(self, model: MultiAdapterModel, router: IPCRRouter):
        self.model = model
        self.router = router
        self.metrics = {
            "classification": evaluate.load("accuracy"),
            "generation": evaluate.load("rouge"),
            "qa": evaluate.load("exact_match"),
        }

    def evaluate_routing(
        self, samples: list[dict], mode: str,  # mode: "oracle" | "ipcr" | "uniform" | "random"
    ) -> list[dict]:
        """Per-sample: select adapter per mode, generate, return {pred, ref, task_type}."""
        ...

    def compute_metrics(self, results: list[dict]) -> dict[str, float]:
        """Group results by task_type, apply matching metric, return {task_family: score}."""
        ...

    def compare_significance(self, ipcr_scores: list[float], uniform_scores: list[float]) -> dict:
        """Paired t-test. Returns {"t_stat": float, "p_value": float, "significant": bool}."""
        t_stat, p_value = stats.ttest_rel(ipcr_scores, uniform_scores)
        return {"t_stat": t_stat, "p_value": p_value, "significant": p_value < 0.05}
```

### Pseudo-code (evaluate_routing, mode dispatch)

```
for sample in samples:
    if mode == "oracle": adapter = sample["true_task_family"]
    elif mode == "ipcr": adapter = router.route(sample["instruction"])
    elif mode == "uniform": model.set_uniform(); adapter = None
    elif mode == "random": adapter = random.choice(model.adapter_names)
    if adapter: model.set_adapter(adapter)
    pred = model.generate(sample["instruction"])
    results.append({pred, ref: sample["reference"], task_type: sample["task_type"]})
return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | evaluate_routing() | Mode-dispatch generation loop (oracle/ipcr/uniform/random) |
| L-4-2 | compute_metrics() + compare_significance() | Task-typed scoring + paired t-test vs uniform |

---

## Tensor Shape Specifications (Summary)

| Variable | Shape | Note |
|----------|-------|------|
| instruction_embedding | [384] | all-MiniLM-L6-v2 |
| batch_embeddings | [B, 384] | route_batch |
| probe_logits | [B, k] | k=8 adapters |
| adapter_weights (uniform) | [k] | all = 1/k |
| generated_ids | [B, T] | model.generate output |

---

**Subtask total: 8/8 used**
