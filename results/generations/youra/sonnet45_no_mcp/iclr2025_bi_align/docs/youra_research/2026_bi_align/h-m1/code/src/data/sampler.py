"""
Stratified sampling from HH-RLHF dataset.
"""
import pandas as pd
import numpy as np
from datasets.arrow_dataset import Dataset


def stratified_sample(
    dataset: Dataset,
    sample_size: int = 500,
    strata_column: str = "length_quartile",
    seed: int = 42
) -> pd.DataFrame:
    """
    Perform stratified random sampling from HH-RLHF dataset.

    Args:
        dataset: HuggingFace Dataset object (rejected responses only)
        sample_size: Total number of samples to draw (default 500)
        strata_column: Column name for stratification (default "length_quartile")
        seed: Random seed for reproducibility (default 42)

    Returns:
        pd.DataFrame with columns: [id, prompt, rejected_response, length, length_quartile]
        Shape: (500, 5)

    Algorithm:
        1. Convert HF Dataset to pandas DataFrame
        2. Calculate response lengths
        3. Assign length quartiles (Q1, Q2, Q3, Q4)
        4. Sample equally from each quartile (125 samples per quartile)
        5. Return combined DataFrame
    """
    # Set random seed
    np.random.seed(seed)

    # Convert to DataFrame
    # HH-RLHF dataset only has 'chosen' and 'rejected' columns
    # Extract conversations from rejected responses
    df = pd.DataFrame({
        'rejected_response': dataset['rejected'],
        'chosen_response': dataset['chosen']
    })

    # Add ID column
    df['id'] = range(len(df))

    # Extract prompt from conversation (text before first "Assistant:")
    def extract_prompt(text):
        """Extract the prompt/context from HH-RLHF conversation."""
        if '\n\nAssistant:' in text:
            return text.split('\n\nAssistant:')[0]
        return text[:100]  # Fallback: first 100 chars

    df['prompt'] = df['rejected_response'].apply(extract_prompt)

    # Step 1: Compute lengths
    df['length'] = df['rejected_response'].apply(len)

    # Step 2: Assign quartiles
    df['length_quartile'] = pd.qcut(
        df['length'],
        q=4,
        labels=["Q1", "Q2", "Q3", "Q4"],
        duplicates='drop'
    )

    # Step 3: Stratified sampling
    samples_per_quartile = sample_size // 4  # 125

    sampled = df.groupby('length_quartile', group_keys=False, observed=True).apply(
        lambda x: x.sample(n=min(samples_per_quartile, len(x)), random_state=seed)
    )

    # Reset index
    sampled = sampled.reset_index(drop=True)

    # Ensure we have exactly sample_size samples (handle edge cases)
    if len(sampled) < sample_size:
        # If we don't have enough samples in quartiles, sample more from available data
        remaining = sample_size - len(sampled)
        additional = df[~df['id'].isin(sampled['id'])].sample(n=remaining, random_state=seed)
        sampled = pd.concat([sampled, additional]).reset_index(drop=True)
    elif len(sampled) > sample_size:
        # If we have too many, randomly select sample_size
        sampled = sampled.sample(n=sample_size, random_state=seed).reset_index(drop=True)

    return sampled[['id', 'prompt', 'rejected_response', 'length', 'length_quartile']]
