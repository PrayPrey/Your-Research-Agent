# Training-Time Lyapunov-Certified Diffusion Controllers with Probabilistic Stability Guarantees

## Motivation
Safety-critical control applications (robotics, autonomous vehicles, aerospace) require formal stability guarantees, yet state-of-the-art diffusion-based controllers either lack theoretical certificates or impose them at inference-time with significant computational overhead. Existing methods like S²Diff achieve only ~80% stability satisfaction and require expensive guidance at every sampling step. This creates a critical gap: how to achieve both high-performance flexible control AND provable stability guarantees efficiently.

## Main Idea
We propose **training-time Lyapunov integration** (TLCD-PSG) that embeds Control Lyapunov Functions directly into diffusion model training via a dual-network architecture. A Score Network learns control policies while a Lyapunov Network provides stability certificates, jointly optimized through L_total = L_diffusion + λ(t)·L_Lyap with curriculum learning. This "bakes" stability into the learned score function itself, eliminating inference-time guidance overhead.

**Key mechanism**: Three-phase curriculum gradually increases stability weight λ from 0 to λ_max, preventing mode collapse while ensuring probabilistic Lyapunov decrease (V̇ < -αV).

**Expected outcomes**: ≥95% stability satisfaction (vs S²Diff's 80%), 2-3x faster sampling, within 10% task performance of unconstrained policies, with only 30% training overhead. This enables real-time safety-critical control with formal certificates.