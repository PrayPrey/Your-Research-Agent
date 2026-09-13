"""Training loop for H-M3: LoRA Fine-tuning on WikiText-103.

Reused from H-M2 with identical implementation.
Implements:
- WikiText-103 loading and tokenization
- DataLoader construction with chunking
- AdamW optimizer with cosine scheduler
- Gradient accumulation training loop
"""

from typing import List, Tuple

import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from config import ExperimentConfig


def load_wikitext103_train(config: ExperimentConfig, tokenizer):
    """Load and tokenize WikiText-103 train split; chunk to max_seq_length.

    Args:
        config: Experiment configuration
        tokenizer: Tokenizer for text encoding

    Returns:
        HuggingFace Dataset with 'input_ids' column
    """
    from datasets import load_dataset

    print(f"Loading WikiText-103 train split...")
    dataset = load_dataset(
        config.dataset_name,
        config.dataset_config,
        split="train"
    )

    # Filter empty texts
    dataset = dataset.filter(lambda x: len(x["text"].strip()) > 0)

    print(f"Tokenizing {len(dataset)} examples...")

    def tokenize_and_chunk(examples):
        """Tokenize text and create fixed-length chunks."""
        # Tokenize all texts
        tokenized = tokenizer(
            examples["text"],
            truncation=False,
            padding=False,
            return_attention_mask=False,
        )

        # Concatenate all tokens
        all_input_ids = []
        for ids in tokenized["input_ids"]:
            all_input_ids.extend(ids)

        # Chunk into fixed-length sequences
        chunks = []
        for i in range(0, len(all_input_ids) - config.max_seq_length, config.max_seq_length):
            chunks.append(all_input_ids[i:i + config.max_seq_length])

        return {"input_ids": chunks}

    # Process in batches for efficiency
    tokenized_dataset = dataset.map(
        tokenize_and_chunk,
        batched=True,
        batch_size=1000,
        remove_columns=dataset.column_names,
        desc="Tokenizing",
    )

    print(f"Created {len(tokenized_dataset)} sequences of length {config.max_seq_length}")

    # Subsample for PoC speed
    if config.num_train_sequences and len(tokenized_dataset) > config.num_train_sequences:
        tokenized_dataset = tokenized_dataset.select(range(config.num_train_sequences))
        print(f"Subsampled to {len(tokenized_dataset)} sequences for PoC")

    return tokenized_dataset


def build_dataloader(tokenized_dataset, config: ExperimentConfig) -> DataLoader:
    """Build DataLoader with batch_size, collate, shuffle=True.

    Args:
        tokenized_dataset: Dataset with 'input_ids' column
        config: Experiment configuration

    Returns:
        DataLoader yielding batches of {'input_ids': Tensor[B, L]}
    """
    def collate_fn(batch):
        input_ids = torch.tensor([item["input_ids"] for item in batch], dtype=torch.long)
        return {"input_ids": input_ids}

    dataloader = DataLoader(
        tokenized_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        collate_fn=collate_fn,
        num_workers=0,  # Avoid multiprocessing issues
        pin_memory=True,
    )

    return dataloader


def build_optimizer_and_scheduler(
    model,
    config: ExperimentConfig,
    num_training_steps: int,
) -> Tuple:
    """Build AdamW optimizer and cosine scheduler with warmup.

    Args:
        model: PEFT model with trainable LoRA parameters
        config: Experiment configuration
        num_training_steps: Total number of optimizer steps

    Returns:
        (optimizer, scheduler) tuple
    """
    from torch.optim import AdamW
    from transformers import get_cosine_schedule_with_warmup

    # Only optimize trainable parameters (LoRA adapters)
    optimizer = AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )

    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=config.warmup_steps,
        num_training_steps=num_training_steps,
    )

    return optimizer, scheduler


def train(
    model,
    dataloader: DataLoader,
    optimizer,
    scheduler,
    config: ExperimentConfig,
) -> List[float]:
    """Run training loop with gradient accumulation.

    Args:
        model: PEFT model ready for training
        dataloader: Training data loader
        optimizer: AdamW optimizer
        scheduler: Learning rate scheduler
        config: Experiment configuration

    Returns:
        List of per-step loss values
    """
    device = torch.device(config.device)
    model.train()

    losses = []
    global_step = 0
    accumulation_steps = config.gradient_accumulation_steps

    print(f"\nStarting training:")
    print(f"  Epochs: {config.num_epochs}")
    print(f"  Batch size: {config.batch_size}")
    print(f"  Gradient accumulation: {accumulation_steps}")
    print(f"  Effective batch size: {config.batch_size * accumulation_steps}")
    print(f"  Learning rate: {config.learning_rate}")

    for epoch in range(config.num_epochs):
        epoch_loss = 0.0
        num_batches = 0

        progress_bar = tqdm(
            dataloader,
            desc=f"Epoch {epoch + 1}/{config.num_epochs}",
            leave=True,
        )

        for step, batch in enumerate(progress_bar):
            input_ids = batch["input_ids"].to(device)

            # Forward pass with labels for LM loss
            outputs = model(input_ids=input_ids, labels=input_ids)
            loss = outputs.loss / accumulation_steps

            # Backward pass
            loss.backward()

            # Record loss (unscaled)
            step_loss = loss.item() * accumulation_steps
            losses.append(step_loss)
            epoch_loss += step_loss
            num_batches += 1

            # Gradient accumulation
            if (step + 1) % accumulation_steps == 0:
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                global_step += 1

            # Update progress bar
            progress_bar.set_postfix({
                'loss': f'{step_loss:.4f}',
                'avg_loss': f'{epoch_loss / num_batches:.4f}',
                'lr': f'{scheduler.get_last_lr()[0]:.2e}',
            })

        avg_epoch_loss = epoch_loss / num_batches
        print(f"Epoch {epoch + 1} completed. Average loss: {avg_epoch_loss:.4f}")

    model.eval()
    print(f"\nTraining complete. Total steps: {len(losses)}")

    return losses
