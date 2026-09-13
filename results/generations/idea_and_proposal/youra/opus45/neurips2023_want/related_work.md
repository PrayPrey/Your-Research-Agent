## Related Work

**Related Papers**
1. **Title**: Colossal-Auto: Unified Automation of Parallelization and Activation Checkpoint (arXiv:2023)
   - **Authors**: Liu et al.
   - **Summary**: Demonstrates that joint optimization of parallelism and checkpointing is effective for distributed training, providing a foundation for multi-objective optimization approaches.
   - **Year**: 2023

2. **Title**: Characterizing Power Management Opportunities for LLMs in the Cloud (ASPLOS 2024)
   - **Authors**: Patel et al. (Microsoft)
   - **Summary**: Shows that LLM inference offers substantial headroom for power oversubscription, with POLCA achieving 30% more server deployment through power management.
   - **Year**: 2024

3. **Title**: Profiling & Monitoring Deep Learning Training Tasks (EuroMLSys 2023)
   - **Authors**: Yousefzadeh-Asl-Miandoab et al.
   - **Summary**: Demonstrates that nvidia-smi and DCGM enable accurate resource monitoring for deep learning workloads with low overhead.
   - **Year**: 2023

4. **Title**: DeepSpeed ZeRO
   - **Authors**: Rajbhandari et al.
   - **Summary**: Introduces memory optimization through parameter, gradient, and optimizer state sharding for distributed training.
   - **Year**: 2020

5. **Title**: PyTorch FSDP
   - **Authors**: Not specified
   - **Summary**: Provides native distributed training capabilities with various sharding strategies for memory-efficient training.
   - **Year**: Not specified

6. **Title**: Towards Energy-efficient Deep Learning: Overview of Approaches
   - **Authors**: Mehlin et al.
   - **Summary**: Provides an overview of energy optimization approaches in deep learning, finding that energy optimization is typically isolated from memory and communication optimization.
   - **Year**: 2023

7. **Title**: Uncovering Energy-Efficient Practices in Deep Learning Training
   - **Authors**: Yarally et al.
   - **Summary**: Investigates energy-efficient practices in deep learning training, finding that energy-accuracy tradeoffs are not integrated with parallelism strategies.
   - **Year**: 2023

8. **Title**: NSGA-II
   - **Authors**: Deb et al.
   - **Summary**: Introduces a multi-objective optimization algorithm using non-dominated sorting, widely used for discovering Pareto-optimal solutions.
   - **Year**: 2002

**Key Challenges**
1. **Isolated Energy Optimization**: Energy optimization approaches in deep learning are typically treated separately from memory and communication optimization, preventing holistic system efficiency.

2. **Lack of Energy-Parallelism Integration**: Energy-accuracy tradeoffs are not integrated with parallelism strategies, missing opportunities for joint optimization in distributed training.

3. **Multi-Objective Optimization Gap**: Existing frameworks like Colossal-Auto optimize parallelism and checkpointing jointly but do not extend to include energy as an optimization objective.

4. **Fragmented Optimization Approaches**: Current solutions address individual aspects (memory via ZeRO/FSDP, power management for inference) but lack unified frameworks for training that consider energy, memory, and communication together.
