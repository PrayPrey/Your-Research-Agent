import json
import config


def evaluate_gate(resnet_bias, vgg_bias):
    """Direction + effect-size threshold gate."""
    diff = resnet_bias["texture_bias_ratio"] - vgg_bias["texture_bias_ratio"]
    pass_gate = diff > config.EFFECT_SIZE_THRESHOLD

    return {
        "pass_gate": pass_gate,
        "diff": diff,
        "resnet_ratio": resnet_bias["texture_bias_ratio"],
        "vgg_ratio": vgg_bias["texture_bias_ratio"],
        "threshold": config.EFFECT_SIZE_THRESHOLD,
    }


def write_gate_report(gate_result, path):
    with open(path, 'w') as f:
        json.dump(gate_result, f, indent=2)
