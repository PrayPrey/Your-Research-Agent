# Title
Hyena-Hamiltonian World Models: Scalable Physics-Consistent Long-Horizon Prediction for Robotics

# Motivation
Current world models face a critical trade-off: transformers achieve high-quality predictions but scale quadratically (O(T²)), limiting them to ~256 frames, while existing long-horizon methods suffer from physics violations (25-35% violation rates) that accumulate over time. This prevents reliable long-horizon planning in robotics where 1000+ frame predictions with physical consistency are essential for model-based reinforcement learning and sim-to-real transfer. No existing approach simultaneously addresses computational scalability and physics consistency at extended horizons.

# Main Idea
We propose combining **Hyena operators** (sub-quadratic O(T log T) long convolutions from genomics) with **Hamiltonian Neural ODE constraints** to achieve scalable, physics-consistent 1000+ frame world models. The architecture uses Hyena's implicit convolutions for efficient long-range temporal modeling while Hamiltonian dynamics with symplectic integration guarantees energy conservation by construction, preventing physics violations.

**Key predictions**: (1) 10-15x training speedup versus transformers at matched quality, (2) 40-60% reduction in physics violations through energy-conserving constraints, (3) successful 1000-frame rollouts in robotic manipulation domains. We validate through controlled ablations isolating Hyena's scalability contribution, Hamiltonian's physics enforcement, and cross-domain transfer effectiveness, comparing against transformer, SSM, and diffusion baselines. This enables practical long-horizon planning for robotics within standard GPU memory constraints.