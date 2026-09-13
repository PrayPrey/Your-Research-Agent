# 4. Experimental Setup

## 4.1 Research Questions

We design our experiments to answer three questions directly motivated by the conditionality hypothesis:

**RQ1:** Does epoch-5 k-means clustering on pretrained ResNet-50 ERM embeddings recover spurious group structure for datasets with visually dominant, scene-level spurious features? (Waterbirds)

**RQ2:** Does the same pipeline succeed for datasets with fine-grained, texture-based spurious features? (CelebA)

**RQ3:** Is any observed performance gap a genuine reflection of feature-strength conditionality, or is it attributable to experimental confounds (implementation error, hyperparameter sensitivity, metric artifacts)?

RQ1 and RQ2 map directly to the two predictions of the conditionality hypothesis. RQ3 is addressed through experimental design integrity: identical code, identical hyperparameters, and random baseline computation.

## 4.2 Datasets

**Waterbirds** is constructed from the Caltech-UCSD Birds-200-2011 dataset with backgrounds from the Places dataset [Sagawa et al., 2020]. It contains 4,795 training samples with a 95% spurious correlation between bird type (waterbird/landbird) and background (water/land). There are 4 groups: waterbird-on-water (dominant majority), waterbird-on-land (minority), landbird-on-land (dominant majority), landbird-on-water (minority).

**CelebA** [Liu et al., 2015] contains 162,770 training samples of celebrity faces. We use the binary hair color prediction task (blonde vs. non-blonde) with sex as the spurious attribute. The dataset is approximately 80% non-blonde, creating a class imbalance. The spurious correlation between blonde hair and female sex is strong in the training data.

| Dataset | Train samples | Spurious attribute | Feature type | ImageNet alignment |
|---|---|---|---|---|
| Waterbirds | 4,795 | Background habitat | Global scene-level | High (scene categories) |
| CelebA | 162,770 | Biological sex | Local texture (hair) | Low (no hair-color category) |

## 4.3 Baselines

**Random clustering baseline:** We compute AMI and worst-cluster purity for randomly shuffled cluster assignments (preserving cluster sizes). This establishes the floor against which meaningful clustering results are measured. Results: Waterbirds random AMI≈0.0001, random purity=0.727; CelebA random AMI≈0.000, random purity=0.440.

The random purity baseline differs substantially between datasets because it is driven by the class distribution (a dataset with a 80/20 class split has random purity≈0.80 for the dominant cluster, lower when averaged). We report worst-cluster purity to penalize solutions that achieve good average purity by collapsing the minority class.

## 4.4 Implementation Details

All experiments are implemented in PyTorch. ResNet-50 is loaded from `torchvision.models.resnet50(pretrained=True)`. The penultimate layer is defined as the output of the global average pooling layer (dimension 2048). K-means is implemented via `sklearn.cluster.KMeans` with `n_init=10` and `random_state=42`. AMI is computed via `sklearn.metrics.adjusted_mutual_info_score`. Worst-cluster purity is computed as `min over clusters of: (majority group count in cluster) / (cluster size)`.

Training uses SGD with momentum=0.9, lr=1e-3, weight\_decay=1e-3, batch\_size=32. Training runs for exactly 5 epochs. Embeddings are extracted from the full training set after epoch 5 without augmentation (inference mode, center crop only).

Code is organized as:
- `code/data/datasets.py` — Waterbirds and CelebA dataloaders with group metadata
- `code/models/resnet.py` — ResNet-50 with penultimate-layer extraction
- `code/train.py` — ERM training loop with epoch-5 checkpoint
- `code/extract.py` — Embedding extraction in inference mode
- `code/cluster.py` — K-means, AMI, worst-cluster purity computation
- `code/evaluate.py` — Gate evaluation and results reporting

**Compute:** Experiments run on a single GPU. Waterbirds training + extraction: ~15 minutes. CelebA training + extraction: ~90 minutes (due to larger dataset size).

## 4.5 Evaluation Metrics

**Adjusted Mutual Information (AMI)** measures the agreement between cluster assignments and ground-truth group labels, adjusted for random chance:

$$\text{AMI}(U, V) = \frac{\text{MI}(U,V) - \mathbb{E}[\text{MI}(U,V)]}{\text{avg}(H(U), H(V)) - \mathbb{E}[\text{MI}(U,V)]}$$

AMI=0 corresponds to independent assignments; AMI=1 corresponds to perfect agreement. The chance-adjustment makes AMI meaningful even when cluster sizes differ. **Threshold: AMI ≥ 0.5**, following [Bao et al., 2022].

**Worst-Cluster Purity** measures the minimum fraction of samples from the majority group within any single cluster. A high worst-cluster purity indicates that every cluster is dominated by one spurious group — the desired outcome for downstream group-based robustification. **Threshold: purity ≥ 0.75**, following [Bao et al., 2022].

Both metrics are evaluated against ground-truth group labels used only for evaluation. Together they provide complementary perspectives: AMI captures overall information-theoretic alignment; worst-cluster purity captures the worst-case practical quality of a cluster as a proxy label.
