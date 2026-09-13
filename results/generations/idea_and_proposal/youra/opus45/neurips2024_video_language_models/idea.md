# Research Idea

## Title
PhysTac: Physics-Informed Disentangled Representations for Cross-Sensor Tactile Transfer

## Motivation
Vision-based tactile sensors are transforming robotic manipulation, yet each sensor type (GelSight, DIGIT, TacTip) produces visually distinct outputs despite sensing identical physical phenomena—contact geometry and forces. Current cross-sensor transfer methods (T3, AnyTouch) rely on data-driven alignment requiring extensive labeled data from each new sensor, creating deployment bottlenecks. The key insight is that contact mechanics is sensor-agnostic; only the optical encoding differs. This gap motivates a physics-grounded approach to representation learning.

## Main Idea
We propose PhysTac, a dual-branch architecture that disentangles physics-invariant contact features from sensor-specific appearance features. The physics branch learns contact geometry (deformation fields, force distributions) supervised by Finite Element Method simulations, while the appearance branch captures sensor-specific optical characteristics. Gradient Reversal Layers and mutual information minimization enforce separation between branches.

**Core mechanism:** By grounding representations in physical contact properties rather than visual statistics, features become inherently transferable across sensors sharing similar elastomer physics.

**Methodology:** Train on multi-sensor dataset (FoTa, 3M+ samples) with FEM-derived labels; evaluate zero-shot and few-shot transfer on TacBench.

**Expected outcomes:** >10% zero-shot accuracy improvement over T3 baseline; 10× sample efficiency for new sensor adaptation. This enables rapid deployment of tactile intelligence on novel sensor hardware with minimal data collection.