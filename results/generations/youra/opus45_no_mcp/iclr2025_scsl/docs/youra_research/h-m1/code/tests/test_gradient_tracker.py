import torch
from torch import nn
import sys
sys.path.insert(0, '..')
from gradient_tracker import GradientTracker

def test_hook_registration():
    model = nn.Sequential(nn.Linear(10, 5))
    model.fc = model[0]
    tracker = GradientTracker(model)
    assert tracker._hook_handle is not None
    tracker.remove()

def test_group_gradient_ratio():
    fc = nn.Linear(10, 2)
    model = nn.Module()
    model.fc = fc
    model.forward = fc.forward
    tracker = GradientTracker(model, majority_group=0, minority_group=3)
    x = torch.randn(8, 10)
    y = torch.randint(0, 2, (8,))
    groups = torch.tensor([0, 0, 0, 0, 3, 3, 1, 1])
    out = fc(x)
    loss = nn.CrossEntropyLoss()(out, y)
    loss.backward()
    ratio, norms = tracker.compute_group_gradient_ratio(groups)
    assert ratio is not None
    assert 0 in norms and 3 in norms
    tracker.remove()

def test_missing_group_returns_none():
    fc = nn.Linear(10, 2)
    model = nn.Module()
    model.fc = fc
    tracker = GradientTracker(model, majority_group=0, minority_group=3)
    x = torch.randn(4, 10)
    y = torch.randint(0, 2, (4,))
    groups = torch.tensor([0, 0, 1, 1])
    out = fc(x)
    loss = nn.CrossEntropyLoss()(out, y)
    loss.backward()
    ratio, norms = tracker.compute_group_gradient_ratio(groups)
    assert ratio is None
    tracker.remove()

def test_epoch_logging():
    model = nn.Sequential(nn.Linear(10, 2))
    model.fc = model[0]
    tracker = GradientTracker(model)
    tracker.log_epoch_gradients(0, 0.5, {0: 1.0, 3: 0.5})
    assert len(tracker.gradient_history) == 1
    assert tracker.gradient_history[0]['gradient_ratio'] == 0.5
    tracker.remove()

if __name__ == "__main__":
    test_hook_registration()
    test_group_gradient_ratio()
    test_missing_group_returns_none()
    test_epoch_logging()
    print("All tests passed")
