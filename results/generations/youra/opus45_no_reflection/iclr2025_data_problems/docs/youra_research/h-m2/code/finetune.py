import torch
import torch.nn as nn
from torch.optim import AdamW
from tqdm import tqdm
import os

def finetune(model, train_loader, epochs, lr, device):
    model = model.to(device)
    model.train()
    optimizer = AdamW(model.parameters(), lr=lr)

    for epoch in range(epochs):
        total_loss = 0
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"Epoch {epoch+1} avg loss: {total_loss / len(train_loader):.4f}")

    return model

def save_checkpoint(model, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(model.state_dict(), path)

def load_checkpoint(model, path, device):
    model.load_state_dict(torch.load(path, map_location=device))
    return model
