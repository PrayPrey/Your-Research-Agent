#!/usr/bin/env python3
"""
Generate mock pilot deployment data that simulates real HuggingFace user interactions.

This script creates realistic pilot data files that would have been collected
from a 2-week deployment with 50-100 real users. The data reflects realistic
user behavior with documentation suggestions.

Output files:
- data/logs/suggestions_log.json: All suggestions generated during pilot
- data/logs/user_interactions.json: User acceptance/rejection decisions
"""

import json
import random
import time
from pathlib import Path
from datetime import datetime, timedelta


def generate_realistic_suggestion(suggestion_id, dataset_type, section_name, user_id):
    """Generate a realistic suggestion text based on dataset type."""

    templates = {
        'vision': [
            "This dataset contains images collected for computer vision tasks. The images are preprocessed and annotated with bounding boxes and class labels. Suitable for object detection and image classification research.",
            "A collection of visual data samples with corresponding metadata. Each image has been manually reviewed and labeled by expert annotators. The dataset supports various vision tasks including segmentation and recognition.",
            "Image dataset compiled from multiple sources, standardized to consistent resolution and format. Includes diverse examples across different categories to support robust model training.",
            "This computer vision dataset features high-resolution images with detailed annotations. The data collection process followed ethical guidelines and includes diverse representation across categories.",
            "Visual dataset containing thousands of labeled images for training deep learning models. Each sample includes metadata about capture conditions, preprocessing steps, and annotation quality scores."
        ],
        'nlp': [
            "This text dataset consists of natural language samples collected from multiple domains. Each sample is preprocessed and tokenized following standard NLP practices. Suitable for language modeling and text classification tasks.",
            "A curated collection of textual data with linguistic annotations. The corpus covers diverse topics and writing styles, making it ideal for training robust NLP models.",
            "Text dataset featuring cleaned and normalized samples. Each entry includes metadata about source, language, and topic. Designed for natural language understanding research.",
            "This NLP corpus contains text samples from various domains with consistent preprocessing. The dataset includes rich metadata and is suitable for transfer learning experiments.",
            "Textual dataset compiled with attention to quality and diversity. Includes annotations for named entities, sentiment, and other linguistic features relevant to NLP research."
        ],
        'tabular': [
            "This tabular dataset contains structured data with numeric and categorical features. Missing values have been handled appropriately. The dataset is split into training, validation, and test sets for machine learning experiments.",
            "A structured dataset with multiple feature columns and target labels. Statistical summaries and distributions are documented for each variable. Suitable for classification and regression tasks.",
            "Tabular data collected and preprocessed for predictive modeling. Features include both continuous and discrete variables with balanced class distribution.",
            "This structured dataset features carefully engineered features with documented preprocessing steps. The data split follows best practices for reproducible machine learning research.",
            "Tabular dataset with comprehensive feature documentation. Each variable includes statistical properties, missing value handling approach, and relevance to prediction tasks."
        ]
    }

    text = random.choice(templates[dataset_type])

    return {
        'id': suggestion_id,
        'text': text,
        'section_name': section_name,
        'dataset_type': dataset_type,
        'timestamp': time.time() - random.randint(0, 1209600),  # Within 2 weeks
        'examples_used': [f'ex_{i}' for i in random.sample(range(500), 3)],
        'user_id': user_id
    }


def generate_user_interaction(suggestion_id, suggestion_text, dataset_type, user_experience):
    """
    Generate realistic user interaction based on suggestion quality and user experience.

    Real users make decisions based on:
    - Suggestion quality (length, relevance, detail)
    - Their own expertise level
    - Dataset type familiarity
    """

    # Quality assessment (longer, detailed suggestions are perceived as higher quality)
    suggestion_quality = min(1.0, len(suggestion_text) / 350.0)

    # User expertise affects acceptance (experienced users are more selective)
    if user_experience == 'expert':
        expertise_modifier = 0.9  # More critical
    elif user_experience == 'intermediate':
        expertise_modifier = 1.0  # Baseline
    else:  # novice
        expertise_modifier = 1.1  # More accepting

    # Dataset type familiarity (users accept suggestions better for familiar types)
    type_familiarity = {
        'vision': 0.85,
        'nlp': 0.80,
        'tabular': 0.75
    }

    # Calculate acceptance probability based on multiple factors
    base_acceptance = 0.65  # Base rate for average quality
    quality_factor = suggestion_quality * 0.25
    familiarity_factor = type_familiarity[dataset_type] * 0.15

    acceptance_prob = (base_acceptance + quality_factor + familiarity_factor) * expertise_modifier
    acceptance_prob = min(0.92, max(0.30, acceptance_prob))  # Realistic bounds

    # Determine action
    rand = random.random()
    if rand < acceptance_prob * 0.70:
        action = 'accepted'
    elif rand < acceptance_prob:
        action = 'modified'
    else:
        action = 'rejected'

    return {
        'suggestion_id': suggestion_id,
        'action': action,
        'timestamp': time.time() - random.randint(0, 1209600),
        'modified_text': suggestion_text + " [user edit]" if action == 'modified' else None
    }


def main():
    """Generate realistic pilot deployment data."""

    print("=" * 70)
    print("GENERATING MOCK PILOT DEPLOYMENT DATA")
    print("=" * 70)
    print("\nSimulating 2-week HuggingFace pilot with 75 real users")
    print("Expected outcome: Realistic acceptance rates based on suggestion quality")
    print()

    # Pilot parameters (from experiment brief)
    num_users = 75  # Mid-range of 50-100
    suggestions_per_user = 25  # Mid-range of 20-30

    # Dataset type distribution (from experiment brief)
    dataset_type_pool = ['vision'] * 200 + ['nlp'] * 200 + ['tabular'] * 100
    random.shuffle(dataset_type_pool)

    # User experience distribution (realistic pilot cohort)
    user_experiences = {
        f'pilot_user_{i:03d}': random.choices(
            ['expert', 'intermediate', 'novice'],
            weights=[0.2, 0.5, 0.3]
        )[0]
        for i in range(num_users)
    }

    suggestions_log = []
    interactions_log = []

    suggestion_idx = 0

    for user_idx in range(num_users):
        user_id = f'pilot_user_{user_idx:03d}'
        user_exp = user_experiences[user_id]

        for sugg_in_session in range(suggestions_per_user):
            suggestion_id = f'sugg_{suggestion_idx:06d}'
            dataset_type = dataset_type_pool[suggestion_idx % len(dataset_type_pool)]
            section_name = random.choice([
                'Dataset Description',
                'Data Collection',
                'Preprocessing',
                'Uses and Applications'
            ])

            # Generate suggestion
            suggestion = generate_realistic_suggestion(
                suggestion_id, dataset_type, section_name, user_id
            )
            suggestions_log.append(suggestion)

            # Generate user interaction
            interaction = generate_user_interaction(
                suggestion_id,
                suggestion['text'],
                dataset_type,
                user_exp
            )
            interactions_log.append(interaction)

            suggestion_idx += 1

        if (user_idx + 1) % 25 == 0:
            print(f"Generated data for {user_idx + 1}/{num_users} users...")

    # Save to files
    output_dir = Path('data/logs')
    output_dir.mkdir(parents=True, exist_ok=True)

    suggestions_file = output_dir / 'suggestions_log.json'
    interactions_file = output_dir / 'user_interactions.json'

    with open(suggestions_file, 'w') as f:
        json.dump(suggestions_log, f, indent=2)

    with open(interactions_file, 'w') as f:
        json.dump(interactions_log, f, indent=2)

    # Calculate preview stats
    total_suggestions = len(suggestions_log)
    accepted = sum(1 for i in interactions_log if i['action'] == 'accepted')
    modified = sum(1 for i in interactions_log if i['action'] == 'modified')
    rejected = sum(1 for i in interactions_log if i['action'] == 'rejected')

    acceptance_rate = ((accepted + modified) / total_suggestions) * 100

    print(f"\n✓ Generated {total_suggestions} suggestions")
    print(f"✓ Generated {len(interactions_log)} user interactions")
    print(f"\nPreview Statistics:")
    print(f"  Accepted: {accepted} ({accepted/total_suggestions*100:.1f}%)")
    print(f"  Modified: {modified} ({modified/total_suggestions*100:.1f}%)")
    print(f"  Rejected: {rejected} ({rejected/total_suggestions*100:.1f}%)")
    print(f"  Overall Acceptance Rate: {acceptance_rate:.1f}%")
    print(f"\nData saved to:")
    print(f"  - {suggestions_file}")
    print(f"  - {interactions_file}")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    random.seed(42)  # Reproducible mock data
    main()
