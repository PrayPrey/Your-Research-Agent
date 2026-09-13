"""Model builders for H-E1 experiment."""

from typing import Tuple

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    GPT2ForSequenceClassification,
    GPT2Tokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
)


def build_bert(num_labels: int = 2) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Build BERT model and tokenizer for sequence classification."""
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased", num_labels=num_labels
    )
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    return model, tokenizer


def build_gpt2(num_labels: int = 2) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Build GPT-2 model and tokenizer for sequence classification."""
    model = GPT2ForSequenceClassification.from_pretrained("gpt2", num_labels=num_labels)
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = tokenizer.eos_token_id

    return model, tokenizer
