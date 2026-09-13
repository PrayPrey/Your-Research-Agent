#!/usr/bin/env python3
"""Test single problem evaluation."""
import sys
sys.path.insert(0, '/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_verifai/docs/youra_research/h-m3/code/src')

from loader import load_minif2f_problems
from worker import evaluate_single_problem
from random_sampler import TacticSampler

# Load config
sampler = TacticSampler('config/tactic_distribution.yaml')

# Load problems
problems = load_minif2f_problems('data/mock_test_244.lean')
print(f"Loaded {len(problems)} problems")

# Test first problem
problem_data = (problems[0], 0)
print(f"\nTesting: {problems[0].id}")

result = evaluate_single_problem(
    problem_data,
    sampler,
    budget=15,
    timeout=300
)

print(f"Result: {result}")
