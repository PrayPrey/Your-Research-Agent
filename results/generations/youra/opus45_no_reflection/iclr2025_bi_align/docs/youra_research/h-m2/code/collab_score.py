"""Collaboration score v2 implementation."""
import re
import numpy as np

def compute_collab_score_v2(response: str) -> float:
    """Length-normalized collaboration score measuring agency-preservation signals."""
    if not response or len(response) < 10:
        return 0.0

    response_lower = response.lower()
    word_count = len(response.split())
    if word_count == 0:
        return 0.0

    # Reasoning trace signals
    reasoning_patterns = [
        r'\bbecause\b', r'\bsince\b', r'\btherefore\b',
        r'\bthis means\b', r'\bas a result\b', r'\bso that\b'
    ]
    reasoning_score = sum(len(re.findall(p, response_lower)) for p in reasoning_patterns)

    # Uncertainty acknowledgment signals
    uncertainty_patterns = [
        r'\bi think\b', r'\bmight\b', r'\bcould be\b',
        r'\bperhaps\b', r'\buncertain\b', r'\bpossibly\b'
    ]
    uncertainty_score = sum(len(re.findall(p, response_lower)) for p in uncertainty_patterns)

    # User engagement signals
    engagement_patterns = [
        r'\byou could\b', r'\bconsider\b', r'\boption\b',
        r'\byou might\b', r'\bwhat do you\b'
    ]
    engagement_score = sum(len(re.findall(p, response_lower)) for p in engagement_patterns)
    engagement_score += response.count('?')

    # Explanation depth signals
    depth_patterns = [
        r'\bfirst\b', r'\bsecond\b', r'\bthird\b',
        r'\bstep \d', r'^\d+\.', r'^-\s'
    ]
    depth_score = sum(len(re.findall(p, response_lower, re.MULTILINE)) for p in depth_patterns)

    raw_score = reasoning_score + uncertainty_score + engagement_score + depth_score
    return raw_score / np.sqrt(word_count)


def score_components(response: str) -> dict:
    """Break down raw_score into sub-counts for visualization."""
    if not response or len(response) < 10:
        return {"reasoning": 0, "uncertainty": 0, "engagement": 0, "depth": 0}

    response_lower = response.lower()

    reasoning_patterns = [
        r'\bbecause\b', r'\bsince\b', r'\btherefore\b',
        r'\bthis means\b', r'\bas a result\b', r'\bso that\b'
    ]
    reasoning = sum(len(re.findall(p, response_lower)) for p in reasoning_patterns)

    uncertainty_patterns = [
        r'\bi think\b', r'\bmight\b', r'\bcould be\b',
        r'\bperhaps\b', r'\buncertain\b', r'\bpossibly\b'
    ]
    uncertainty = sum(len(re.findall(p, response_lower)) for p in uncertainty_patterns)

    engagement_patterns = [
        r'\byou could\b', r'\bconsider\b', r'\boption\b',
        r'\byou might\b', r'\bwhat do you\b'
    ]
    engagement = sum(len(re.findall(p, response_lower)) for p in engagement_patterns)
    engagement += response.count('?')

    depth_patterns = [
        r'\bfirst\b', r'\bsecond\b', r'\bthird\b',
        r'\bstep \d', r'^\d+\.', r'^-\s'
    ]
    depth = sum(len(re.findall(p, response_lower, re.MULTILINE)) for p in depth_patterns)

    return {"reasoning": reasoning, "uncertainty": uncertainty, "engagement": engagement, "depth": depth}
