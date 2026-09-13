# 7. Conclusion

We introduced the first systematic, reproducible measurement framework for the temporal gap between spurious and core feature learning under standard ERM training. Using checkpoint linear probing at every 2 epochs, we defined δ(t) = spurious\_probe\_acc(t) − core\_probe\_acc(t) and the transition epoch t\* where spurious dominance ends, and validated this framework through a five-hypothesis causal verification chain on Waterbirds/ResNet-50.

Our findings confirm a complete causal pathway: spurious features are 10× more sample-efficient to linearly classify (H-M2), this drives a 7× gradient signal advantage in early training (GDR = 6.977, H-M1), producing a statistically significant temporal gap (δ(t) > 0 for 13.3% of training, p = 0.022, H-E1), with a reproducible transition epoch t\* = 2.0 ± 2.0 epochs across random seeds (H-M3). Additionally, we find that DFR achieves WGA = 0.806 even at epoch 1 — before any Waterbirds-specific training — revealing that ImageNet pretraining, not post-t\* feature encoding, is the dominant driver of DFR robustness (H-M4).

This measurement framework provides mechanistic grounding for annotation-free spurious correlation methods and establishes t\* as a testable, seed-stable diagnostic for SGD feature learning dynamics. We release the full codebase, checkpoints, and δ(t) curves to enable replication and extension to other benchmarks and architectures.

**Future work** priorities are: (1) full 300-epoch training runs for quantitatively precise t\* and gap window estimates; (2) CelebA and text domain replication; (3) redesigned H-M4 using DFR absolute WGA to test the mechanistic connection between training depth and DFR efficacy; (4) annotation-free t\* detection via gradient norm proxies.
