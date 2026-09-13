import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset, concatenate_datasets


def load_base_model(model_id: str = "mistralai/Mistral-7B-v0.1"):
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    return model, tokenizer


def build_lora_config(rank: int = 16, alpha: int = 32, dropout: float = 0.05) -> LoraConfig:
    return LoraConfig(
        r=rank,
        lora_alpha=alpha,
        lora_dropout=dropout,
        target_modules=["q_proj", "v_proj"],
        task_type=TaskType.CAUSAL_LM,
        bias="none",
    )


def get_answer_token_ids(tokenizer) -> list[int]:
    tokens = [" A", " B", " C", " D"]
    token_ids = []
    for t in tokens:
        ids = tokenizer.encode(t, add_special_tokens=False)
        token_ids.append(ids[-1] if ids else tokenizer.encode(t.strip(), add_special_tokens=False)[-1])
    return token_ids


def format_training_example(item: dict) -> str:
    question = item["question"]
    choices = item["choices"]
    answer_idx = item["answer"]
    answer_letter = chr(ord('A') + answer_idx)

    text = f"Question: {question}\n\n"
    for i, choice in enumerate(choices):
        letter = chr(ord('A') + i)
        text += f"{letter}. {choice}\n"
    text += f"\nAnswer: {answer_letter}"
    return text


def inject_contamination(
    base_model,
    tokenizer,
    contamination_items: Dataset,
    lora_cfg: LoraConfig,
    epochs: int = 3,
    lr: float = 2e-4,
    batch_size: int = 4,
    grad_accum: int = 8,
    output_dir: str = "./lora_output",
):
    if len(contamination_items) == 0:
        peft_model = get_peft_model(base_model, lora_cfg)
        return peft_model

    def tokenize_fn(examples):
        texts = [format_training_example({"question": q, "choices": c, "answer": a})
                 for q, c, a in zip(examples["question"], examples["choices"], examples["answer"])]
        tokenized = tokenizer(texts, truncation=True, max_length=512, padding="max_length")
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    train_ds = contamination_items.map(tokenize_fn, batched=True, remove_columns=contamination_items.column_names)
    train_ds.set_format("torch")

    peft_model = get_peft_model(base_model, lora_cfg)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        learning_rate=lr,
        warmup_steps=100,
        logging_steps=10,
        save_strategy="no",
        fp16=False,
        bf16=True,
        report_to="none",
    )

    trainer = Trainer(
        model=peft_model,
        args=training_args,
        train_dataset=train_ds,
    )

    trainer.train()
    return peft_model
