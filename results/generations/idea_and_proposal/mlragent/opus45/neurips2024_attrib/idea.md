# Title: Training Data Attribution via Gradient-Weighted Influence Sketching

## Motivation
As language models train on billions of examples, understanding which training data drives specific model behaviors becomes computationally intractable using traditional influence functions. Current methods either require prohibitively expensive per-query computations or sacrifice accuracy through crude approximations. This gap prevents practitioners from debugging model failures, detecting data contamination, and curating datasets effectively. We need attribution methods that scale to internet-sized datasets while maintaining meaningful accuracy.

## Main Idea
We propose **Gradient-Weighted Influence Sketching (GWIS)**, a two-stage approach for scalable data attribution. During training, we maintain compact sketches (using count-min sketch variants) that compress gradient information for each training example into fixed-size representations. These sketches are indexed by random projections of gradient directions, enabling efficient retrieval.

At inference time, given a model output to attribute, we compute its gradient signature and query the sketch structure to retrieve candidate influential training examples in O(log n) time. We then perform precise influence computation only on this small candidate set.

Key innovations include: (1) gradient-aware hashing that preserves influence relationships, (2) hierarchical sketches capturing both local and global attribution patterns, and (3) streaming updates compatible with distributed training.

**Expected outcomes:** 1000x speedup over exact influence functions with <5% attribution error, enabling real-time data debugging for billion-parameter models. This directly addresses data contamination detection and targeted data curation for capability improvement.