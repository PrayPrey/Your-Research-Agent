"""Fine-tuning pipeline for H-E1: all model families on GLUE tasks."""
import logging
import os
import json
import warnings
from dataclasses import dataclass

import numpy as np
import torch
from datasets import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    EvalPrediction,
    DataCollatorWithPadding,
)

from data_loader import get_num_labels, GLUE_TASKS

logger = logging.getLogger(__name__)

MODEL_CONFIGS = {
    "bert-base-uncased":                 {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "roberta-base":                      {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "google/electra-base-discriminator": {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "albert-base-v2":                    {"lr": 2e-5, "batch": 32, "family": "encoder"},
    "gpt2":                              {"lr": 5e-5, "batch": 16, "family": "decoder"},
    "facebook/opt-125m":                 {"lr": 5e-5, "batch": 16, "family": "decoder"},
    "facebook/opt-350m":                 {"lr": 5e-5, "batch": 16, "family": "decoder"},
    "t5-base":                           {"lr": 1e-4, "batch": 32, "family": "enc_dec"},
    "facebook/bart-base":                {"lr": 1e-4, "batch": 32, "family": "enc_dec"},
}

TASK_EPOCHS = {
    "sst2": 3, "qnli": 3, "rte": 3,
    "mnli": 5, "qqp": 5,
}

_TEXTATTACK_SHORTCUTS = {
    "bert-base-uncased": {
        "sst2": "textattack/bert-base-uncased-SST-2",
        "mnli": "textattack/bert-base-uncased-MNLI",
        "qqp":  "textattack/bert-base-uncased-QQP",
        "qnli": "textattack/bert-base-uncased-QNLI",
        "rte":  "textattack/bert-base-uncased-RTE",
    },
    "roberta-base": {
        "sst2": "textattack/roberta-base-SST-2",
        "mnli": "textattack/roberta-base-MNLI",
        "qnli": "textattack/roberta-base-QNLI",
        "rte":  "textattack/roberta-base-RTE",
    },
    "google/electra-base-discriminator": {
        "sst2": "howey/electra-base-sst2",
    },
    "albert-base-v2": {
        "sst2": "textattack/albert-base-v2-SST-2",
        "qqp":  "textattack/albert-base-v2-QQP",
        "rte":  "textattack/albert-base-v2-RTE",
    },
    "gpt2": {
        "sst2": "michelecafagna26/gpt2-medium-finetuned-sst2-sentiment",
    },
    "facebook/opt-125m": {
        "sst2": "utahnlp/sst2_facebook_opt-125m_seed-1",
    },
    "facebook/opt-350m": {
        "sst2": "utahnlp/sst2_facebook_opt-350m_seed-1",
    },
    "t5-base": {
        "sst2": "michelecafagna26/t5-base-finetuned-sst2-sentiment",
    },
    "facebook/bart-base": {
        "sst2": "ModelTC/bart-base-sst2",
    },
}


def load_pretrained_glue_checkpoint(model_id: str, task: str):
    return _TEXTATTACK_SHORTCUTS.get(model_id, {}).get(task.lower())


def _get_task_input_columns(task: str) -> list:
    """Return feature column names for a given GLUE task."""
    if task == "sst2":
        return ["sentence"]
    elif task in ("mnli", "rte", "qnli"):
        return ["premise", "hypothesis"] if task in ("mnli", "rte") else ["question", "sentence"]
    elif task == "qqp":
        return ["question1", "question2"]
    return []


def _tokenize_dataset(dataset, tokenizer, task: str, max_length: int = 128):
    cols = _get_task_input_columns(task)
    ds_cols = dataset.column_names if hasattr(dataset, "column_names") else []

    # Detect actual column names from dataset
    if task == "sst2":
        text_col = "sentence" if "sentence" in ds_cols else "text"
        def tokenize_fn(ex):
            return tokenizer(ex[text_col], truncation=True, max_length=max_length)
    elif task in ("mnli", "rte"):
        col1 = "premise" if "premise" in ds_cols else "sentence1"
        col2 = "hypothesis" if "hypothesis" in ds_cols else "sentence2"
        def tokenize_fn(ex):
            return tokenizer(ex[col1], ex[col2], truncation=True, max_length=max_length)
    elif task == "qnli":
        col1 = "question" if "question" in ds_cols else "sentence1"
        col2 = "sentence" if "sentence" in ds_cols else "sentence2"
        def tokenize_fn(ex):
            return tokenizer(ex[col1], ex[col2], truncation=True, max_length=max_length)
    elif task == "qqp":
        col1 = "question1" if "question1" in ds_cols else "sentence1"
        col2 = "question2" if "question2" in ds_cols else "sentence2"
        def tokenize_fn(ex):
            return tokenizer(ex[col1], ex[col2], truncation=True, max_length=max_length)
    else:
        def tokenize_fn(ex):
            return tokenizer(ex["text"], truncation=True, max_length=max_length)

    remove_cols = [c for c in ds_cols if c not in ("label", "labels")]
    tokenized = dataset.map(tokenize_fn, batched=True, remove_columns=remove_cols)

    # Rename label if needed
    if "label" in tokenized.column_names:
        tokenized = tokenized.rename_column("label", "labels")

    tokenized.set_format("torch")
    return tokenized


def _compute_metrics(eval_pred: EvalPrediction) -> dict:
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": float((preds == labels).mean())}


def _setup_decoder_for_clf(model_id: str, num_labels: int):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "left"
    model = AutoModelForSequenceClassification.from_pretrained(
        model_id, num_labels=num_labels
    )
    model.config.pad_token_id = tokenizer.eos_token_id
    return model, tokenizer


def _setup_enc_dec_for_clf(model_id: str, num_labels: int):
    tokenizer = AutoTokenizer.from_pretrained(model_id, legacy=False)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_id, num_labels=num_labels
    )
    return model, tokenizer


def _setup_encoder_for_clf(model_id: str, num_labels: int):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_id, num_labels=num_labels
    )
    return model, tokenizer


def finetune_model(
    model_id: str,
    task: str,
    train_dataset,
    eval_dataset,
    output_dir: str,
    seed: int = 42,
) -> tuple:
    """Returns (checkpoint_path, clean_accuracy)."""
    num_labels = get_num_labels(task)
    family = MODEL_CONFIGS[model_id]["family"]
    lr = MODEL_CONFIGS[model_id]["lr"]
    batch = MODEL_CONFIGS[model_id]["batch"]
    epochs = TASK_EPOCHS.get(task, 3)

    if family == "decoder":
        model, tokenizer = _setup_decoder_for_clf(model_id, num_labels)
    elif family == "enc_dec":
        model, tokenizer = _setup_enc_dec_for_clf(model_id, num_labels)
    else:
        model, tokenizer = _setup_encoder_for_clf(model_id, num_labels)

    train_tok = _tokenize_dataset(train_dataset, tokenizer, task)
    eval_tok = _tokenize_dataset(eval_dataset, tokenizer, task)

    collator = DataCollatorWithPadding(tokenizer)

    ckpt_path = os.path.join(output_dir, model_id.replace("/", "_"), task)
    os.makedirs(ckpt_path, exist_ok=True)

    fp16 = torch.cuda.is_available()
    training_args = TrainingArguments(
        output_dir=ckpt_path,
        num_train_epochs=epochs,
        per_device_train_batch_size=min(batch, 16),
        per_device_eval_batch_size=32,
        learning_rate=lr,
        weight_decay=0.01,
        warmup_ratio=0.10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        seed=seed,
        fp16=fp16,
        report_to="none",
        dataloader_num_workers=0,
        logging_steps=100,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tok,
        eval_dataset=eval_tok,
        tokenizer=tokenizer,
        data_collator=collator,
        compute_metrics=_compute_metrics,
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        trainer.train()

    eval_result = trainer.evaluate()
    clean_acc = eval_result.get("eval_accuracy", 0.0)

    trainer.save_model(ckpt_path)
    tokenizer.save_pretrained(ckpt_path)

    # Save metadata
    meta = {"model_id": model_id, "task": task, "clean_acc": clean_acc, "family": family}
    with open(os.path.join(ckpt_path, "meta.json"), "w") as f:
        json.dump(meta, f)

    logger.info(f"Fine-tuned {model_id}/{task}: acc={clean_acc:.4f} -> {ckpt_path}")
    return ckpt_path, clean_acc


def finetune_all(
    model_ids: list,
    tasks: list,
    data: dict,
    checkpoint_dir: str,
    seed: int = 42,
    skip_finetuning: bool = False,
) -> dict:
    """Returns {model_id: {task: (ckpt_path, clean_acc)}}."""
    results = {}
    for model_id in model_ids:
        results[model_id] = {}
        for task in tasks:
            logger.info(f"Processing {model_id} / {task}")

            hub_id = load_pretrained_glue_checkpoint(model_id, task)
            if hub_id and skip_finetuning:
                logger.info(f"Using pre-trained: {hub_id}")
                results[model_id][task] = (hub_id, None)
                continue

            if skip_finetuning:
                # No shortcut available and skip_finetuning=True → skip this task
                logger.info(f"No shortcut for {model_id}/{task} and skip_finetuning=True, skipping")
                continue

            if task not in data.get("train", {}):
                logger.warning(f"No train data for {task}, skipping")
                continue

            train_ds = data["train"][task]
            eval_ds = data["eval"][task]

            try:
                ckpt_path, clean_acc = finetune_model(
                    model_id, task, train_ds, eval_ds, checkpoint_dir, seed
                )
                results[model_id][task] = (ckpt_path, clean_acc)
            except Exception as e:
                logger.error(f"Fine-tuning failed for {model_id}/{task}: {e}")
                results[model_id][task] = (None, None)

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("MODEL_CONFIGS:", list(MODEL_CONFIGS.keys()))
    print("Shortcuts available:", list(_TEXTATTACK_SHORTCUTS.keys()))
