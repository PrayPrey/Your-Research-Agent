import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import Config
from data import inject_benchmark


class TextDataset(Dataset):
    def __init__(self, texts: list[str], tokenizer, max_len: int):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(self.texts[idx], truncation=True, max_length=self.max_len,
                            padding="max_length", return_tensors="pt")
        return {k: v.squeeze(0) for k, v in enc.items()}


def train_one_run(cfg: Config, corpus: list[str], benchmark: list[dict], injection_rate: float):
    print(f"\n=== Training with injection_rate={injection_rate} ===")
    corpus_c, injected_positions = inject_benchmark(corpus, benchmark, injection_rate, cfg.seed)

    model = AutoModelForCausalLM.from_pretrained(cfg.model_id, torch_dtype=torch.float16)
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.train()

    dataset = TextDataset(corpus_c, tokenizer, cfg.max_seq_len)
    loader = DataLoader(dataset, batch_size=cfg.batch_size // cfg.grad_accum, shuffle=True)

    optimizer = AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, betas=cfg.betas)

    step = 0
    accum_loss = 0.0
    loader_iter = iter(loader)

    while step < cfg.train_steps:
        try:
            batch = next(loader_iter)
        except StopIteration:
            loader_iter = iter(loader)
            batch = next(loader_iter)

        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=input_ids)
        loss = outputs.loss / cfg.grad_accum
        loss.backward()
        accum_loss += loss.item()

        if (step + 1) % cfg.grad_accum == 0:
            optimizer.step()
            optimizer.zero_grad()
            if step % 500 == 0:
                print(f"Step {step}, loss: {accum_loss:.4f}")
            accum_loss = 0.0

        step += 1

    print(f"Training complete for injection_rate={injection_rate}")
    return model, tokenizer, injected_positions
