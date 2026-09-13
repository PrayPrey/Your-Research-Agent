#!/usr/bin/env python3
"""Extract features from h-e1 code and save to cache.
Run from h-e1/code directory with: python ../../h-m2/code/extract_features.py
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../h-e1/code")
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../../h-e1/code")

from data import load_truthfulqa_mc1, build_prompts
from model import load_model, extract_all_scores

OUTPUT_PATH = os.path.dirname(os.path.abspath(__file__)) + "/outputs/h_e1_features.npz"

def main():
    print("Loading TruthfulQA MC1...")
    samples = load_truthfulqa_mc1()
    prompts, labels = build_prompts(samples)
    print(f"Loaded {len(prompts)} prompts")

    print("Loading model...")
    model = load_model()

    print("Extracting scores...")
    scores = extract_all_scores(model, prompts)

    h_l = scores["baseline_entropy"]
    nti = scores["nti"]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    np.savez(OUTPUT_PATH, h_l=h_l, nti=nti, labels=labels)
    print(f"Saved features to {OUTPUT_PATH}")
    print(f"Shape: h_l={h_l.shape}, nti={nti.shape}, labels={labels.shape}")

if __name__ == "__main__":
    main()
