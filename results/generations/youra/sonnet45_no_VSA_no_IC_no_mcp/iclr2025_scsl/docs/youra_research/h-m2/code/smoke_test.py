import torch
import torch.nn as nn
from torch.optim import SGD
from data_loader import get_waterbirds_dataloader
from models import create_resnet_bn

def smoke_test():
    device = 'cpu'
    print(f"Device: {device}")

    print("Loading data...")
    train_loader = get_waterbirds_dataloader('train', batch_size=64, num_workers=2)
    test_loader = get_waterbirds_dataloader('test', batch_size=64, num_workers=2)

    print("Creating model...")
    model = create_resnet_bn()
    model = model.to(device)

    optimizer = SGD(model.parameters(), lr=0.01, momentum=0.9, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    print("Training 1 epoch...")
    model.train()
    for i, batch in enumerate(train_loader):
        images, labels, metadata = batch
        images = images.to(device)
        labels = labels.to(device)

        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        if i >= 5:
            break
        print(f"  Batch {i}: loss={loss.item():.4f}")

    print("Evaluating...")
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for i, batch in enumerate(test_loader):
            images, labels, metadata = batch
            images = images.to(device)
            labels = labels.to(device)

            logits = model(images)
            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

            if i >= 5:
                break

    acc = correct / total
    print(f"Accuracy (6 batches): {acc:.4f}")
    print("Smoke test PASSED")

if __name__ == '__main__':
    smoke_test()
