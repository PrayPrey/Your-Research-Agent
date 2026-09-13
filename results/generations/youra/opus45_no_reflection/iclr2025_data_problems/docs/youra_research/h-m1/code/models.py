"""Model loading for H-M1: BERT and GPT-2 with attention output."""
from transformers import AutoModel, AutoTokenizer


def load_bert() -> tuple:
    """Load BERT-base-uncased with output_attentions=True."""
    model_id = "bert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModel.from_pretrained(model_id, output_attentions=True)
    return model, tokenizer


def load_gpt2() -> tuple:
    """Load GPT-2 with output_attentions=True and pad_token set."""
    model_id = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModel.from_pretrained(model_id, output_attentions=True)
    model.config.pad_token_id = tokenizer.pad_token_id
    return model, tokenizer
