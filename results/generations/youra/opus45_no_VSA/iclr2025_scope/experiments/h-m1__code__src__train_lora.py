"""LoRA adapter training for task-specific fine-tuning."""
import os
import torch
from typing import Dict, List, Optional
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset

class LoRATrainer:
    """Trains task-specific LoRA adapters."""

    def __init__(
        self,
        base_model_id: str,
        lora_rank: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.05,
        target_modules: List[str] = None,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.base_model_id = base_model_id
        self.device = device
        self.lora_config = LoraConfig(
            r=lora_rank,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            target_modules=target_modules or ["q_proj", "v_proj"],
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )
        self._base_model = None
        self._tokenizer = None

    @property
    def tokenizer(self):
        if self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(self.base_model_id)
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
        return self._tokenizer

    def _load_base_model(self):
        if self._base_model is None:
            self._base_model = AutoModelForCausalLM.from_pretrained(
                self.base_model_id,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
            )
        return self._base_model

    def _prepare_dataset(self, samples: List[Dict], max_length: int = 512) -> Dataset:
        """Prepare dataset for training."""
        texts = []
        for s in samples:
            text = f"### Instruction:\n{s['instruction']}\n\n### Response:\n{s['response']}"
            texts.append(text)

        def tokenize_fn(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                max_length=max_length,
                padding="max_length",
            )

        ds = Dataset.from_dict({"text": texts})
        ds = ds.map(tokenize_fn, batched=True, remove_columns=["text"])
        ds = ds.map(lambda x: {"labels": x["input_ids"].copy()}, batched=False)
        return ds

    def train_adapter(
        self,
        task_name: str,
        train_samples: List[Dict],
        output_dir: str,
        epochs: int = 3,
        batch_size: int = 8,
        lr: float = 2e-4,
        max_length: int = 512,
        gradient_accumulation_steps: int = 4,
    ) -> str:
        """Train one LoRA adapter for a task family."""
        base_model = self._load_base_model()
        peft_model = get_peft_model(base_model, self.lora_config)
        peft_model.print_trainable_parameters()

        train_ds = self._prepare_dataset(train_samples, max_length)
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, mlm=False
        )

        adapter_output = os.path.join(output_dir, task_name)
        os.makedirs(adapter_output, exist_ok=True)

        training_args = TrainingArguments(
            output_dir=adapter_output,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            learning_rate=lr,
            weight_decay=0.01,
            warmup_ratio=0.1,
            logging_steps=10,
            save_strategy="epoch",
            fp16=True,
            seed=42,
            report_to=[],
        )

        trainer = Trainer(
            model=peft_model,
            args=training_args,
            train_dataset=train_ds,
            data_collator=data_collator,
        )

        trainer.train()
        peft_model.save_pretrained(adapter_output)
        self.tokenizer.save_pretrained(adapter_output)

        del peft_model
        torch.cuda.empty_cache()

        return adapter_output

    def train_all_adapters(
        self,
        task_family_data: Dict[str, List[Dict]],
        output_root: str,
        **train_kwargs,
    ) -> Dict[str, str]:
        """Train adapters for all task families."""
        adapter_paths = {}
        for task_name, samples in task_family_data.items():
            print(f"Training adapter for {task_name} ({len(samples)} samples)...")
            path = self.train_adapter(task_name, samples, output_root, **train_kwargs)
            adapter_paths[task_name] = path
        return adapter_paths


def train_lora_adapter(
    base_model_id: str,
    task_name: str,
    samples: List[Dict],
    output_dir: str,
    rank: int = 16,
    alpha: int = 32,
    lr: float = 2e-4,
    epochs: int = 3,
    batch_size: int = 8,
) -> str:
    """Convenience function to train single LoRA adapter."""
    trainer = LoRATrainer(
        base_model_id=base_model_id,
        lora_rank=rank,
        lora_alpha=alpha,
    )
    return trainer.train_adapter(
        task_name=task_name,
        train_samples=samples,
        output_dir=output_dir,
        epochs=epochs,
        batch_size=batch_size,
        lr=lr,
    )
