import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer, get_cosine_schedule_with_warmup
from config import Config


class TextDataset(Dataset):
    def __init__(self, texts: list[str], tokenizer, max_len: int):
        self.encodings = []
        for txt in texts:
            enc = tokenizer(txt, truncation=True, max_length=max_len,
                            padding="max_length", return_tensors="pt")
            self.encodings.append({k: v.squeeze(0) for k, v in enc.items()})

    def __len__(self):
        return len(self.encodings)

    def __getitem__(self, idx):
        return self.encodings[idx]


def train_one_run(cfg: Config, corpus: list[str], strategy: str, seed: int) -> tuple:
    """Train model on corpus. Returns (model, tokenizer)."""
    torch.manual_seed(seed)

    print(f"Loading model {cfg.model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
    model = AutoModelForCausalLM.from_pretrained(cfg.model_id)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.pad_token_id

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    dataset = TextDataset(corpus, tokenizer, cfg.seq_len)
    loader = DataLoader(dataset, batch_size=cfg.batch_size, shuffle=True)

    optimizer = torch.optim.AdamW(
        model.parameters(), lr=cfg.lr,
        betas=cfg.betas, eps=cfg.eps, weight_decay=cfg.weight_decay
    )
    scheduler = get_cosine_schedule_with_warmup(
        optimizer, num_warmup_steps=max(1, cfg.train_steps // 10),
        num_training_steps=cfg.train_steps
    )

    model.train()
    step = 0
    data_iter = iter(loader)
    total_loss = 0.0

    print(f"Training [{strategy}] seed={seed} for {cfg.train_steps} steps...")
    while step < cfg.train_steps:
        try:
            batch = next(data_iter)
        except StopIteration:
            data_iter = iter(loader)
            batch = next(data_iter)

        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=input_ids)
        loss = outputs.loss

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
        optimizer.step()
        scheduler.step()

        total_loss += loss.item()
        step += 1

        if step % 10 == 0:
            print(f"  Step {step}/{cfg.train_steps}, Loss: {loss.item():.4f}")

    avg_loss = total_loss / cfg.train_steps
    print(f"Training complete. Avg loss: {avg_loss:.4f}")
    return model, tokenizer
