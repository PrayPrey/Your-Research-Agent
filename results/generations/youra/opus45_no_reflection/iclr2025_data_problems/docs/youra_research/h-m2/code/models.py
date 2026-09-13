from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    GPT2ForSequenceClassification,
    GPT2Tokenizer,
)

def load_bert_classifier(model_id="bert-base-uncased"):
    model = AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=2)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    return model, tokenizer

def load_gpt2_classifier(model_id="gpt2"):
    model = GPT2ForSequenceClassification.from_pretrained(model_id, num_labels=2)
    tokenizer = GPT2Tokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = tokenizer.pad_token_id
    return model, tokenizer
