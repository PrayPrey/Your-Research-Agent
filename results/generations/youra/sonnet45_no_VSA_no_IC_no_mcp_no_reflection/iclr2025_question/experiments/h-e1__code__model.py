import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_llama_model(model_name: str = "meta-llama/Llama-2-7b-hf", device: str = None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.to(device)
    model.eval()

    return model, tokenizer

def forward_pass(model, tokenizer, question: str, max_length: int = 512):
    inputs = tokenizer(question, return_tensors="pt", truncation=True, max_length=max_length)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits[:, -1, :].squeeze(0)
    pred_id = torch.argmax(logits).item()
    pred_text = tokenizer.decode([pred_id])

    return {
        "logits": logits,
        "pred_id": pred_id,
        "pred_text": pred_text
    }
