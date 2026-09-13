---
source_paper: "arxiv_2107_09044.md"
generated_at: "2026-03-16T20:41:38.413395"
model: "gpt-4o-mini"
summary_chars: 5481
---

# Just Train Twice: Improving Group Robustness without Training Group Information

## Key Metadata
- **Authors:** Evan Zheran Liu et al.
- **Year:** 2021
- **Venue:** International Conference on Machine Learning
- **Core Contribution:** Proposes JTT (Just Train Twice), a two-stage training method that improves worst-group accuracy without requiring group annotations on training data.

## Section Summaries

### Abstract
Standard training via empirical risk minimization (ERM) can produce models that achieve high accuracy on average but low accuracy on certain groups, especially in the presence of spurious correlations between the input and label. Prior approaches that achieve high worst-group accuracy, like group distributionally robust optimization (group DRO), require expensive group annotations for each training point, whereas approaches that do not use such group annotations typically achieve unsatisfactory worst-group accuracy. This paper proposes a simple two-stage approach, JTT, that first trains a standard ERM model for several epochs, and then trains a second model that upweights the training examples that the first model misclassifies. Intuitively, this upweights examples from groups on which standard ERM models perform poorly, leading to improved worst-group performance. Averaged over four image classification and natural language processing tasks with spurious correlations, JTT closes 75% of the gap in worst-group accuracy between standard ERM and group DRO, while only requiring group annotations on a small validation set to tune hyperparameters.

### Introduction & Motivation
Empirical risk minimization (ERM) often leads to performance disparities across groups, particularly where spurious correlations exist in the training data. Existing methods that enhance worst-group accuracy, such as group DRO, necessitate obtaining group annotations for every training instance, making them impractical. The proposed JTT method focuses on achieving improved worst-group performance without requiring such extensive annotations, thus addressing a crucial gap in the existing literature.

### Methodology
JTT consists of a two-stage training process:
1. **Identification Stage**: A standard ERM model is trained for a fixed number of epochs \( T \) to identify misclassified examples. This is done using the standard cross-entropy loss function. The error set \( E \) consists of examples misclassified by this model:
   \[
   E = \{ (x_i, y_i) \;|\; \hat{f}_{id}(x_i) \neq y_i \}
   \]
   where \( \hat{f}_{id} \) is the model after \( T \) epochs of training.
   
2. **Upweighting Stage**: A final model \( \hat{f}_{final} \) is trained using the error set examples upweighted. The training loss is modified to reflect this upweighting:
   \[
   J_{up-ERM}(\theta, E) = \lambda_{up} \sum_{(x_i, y_i) \in E} \ell(x_i, y_i; \theta) + \sum_{(x,y) \notin E} \ell(x, y; \theta)
   \]
   where \( \lambda_{up} \) is a hyperparameter that determines the extent of upweighting.

JTT employs a simplified architecture that uses a standard ERM model in both stages. Key hyperparameters include \( T \) (for the identification model) and \( \lambda_{up} \) (for upweighting). The loss functions used during training are standard cross-entropy for both models, and a validation set with group annotations is only needed for hyperparameter tuning.

### Experiments & Results
JTT was evaluated on four datasets with known spurious correlations:
1. **Waterbirds**: 3498 total training examples, group defined by spurious backgrounds.
2. **CelebA**: 202599 total training examples, label correlated with gender.
3. **MultiNLI**: 392702 training examples, classifying sentence entailment, with spurious negation words.
4. **CivilComments-WILDS**: 163262 training examples, relating toxicity of comments to demographic mention.

The models were compared based on average accuracy and worst-group accuracy. Table 1 presents the results:
- **JTT** achieved significant improvements over ERM, with an average worst-group accuracy improvement of 16.2%. 
- JTT closed 75% of the accuracy gap between ERM and group DRO while exhibiting only a 4.2% drop in average accuracy compared to ERM.

Ablation studies revealed that JTT effectively upweights challenging groups identified during the first stage, enhancing the model's performance on these groups. 

### Discussion & Conclusion
JTT outperforms existing methods that require more extensive group information during training, achieving significant improvements in worst-group accuracy while maintaining a high average accuracy. Future work involves better understanding the theoretical underpinnings of JTT and exploring its adaptability to other distribution shifts beyond spurious correlations.

## Key Contributions
- Introduces JTT, a novel two-stage training process for group robustness without needing full group annotations.
- Demonstrates substantial improvements in worst-group accuracy on multiple datasets with spurious correlations.
- Provides empirical analysis supporting the need for minimal group information during validation for effective hyperparameter tuning.

## Potential Relevance
The JTT method could be particularly useful in scenarios where training data lacks group annotations due to high labeling costs. Its findings may inform new methods of addressing disparities in group performance and provide a framework for further exploration of group robustness in other machine learning contexts.