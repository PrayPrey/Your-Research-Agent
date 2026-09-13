## References

$$\bar{\phi}_{t+1} = \tau_h \cdot \bar{\phi}_t + (1 - \tau_h) \cdot \phi_t$$

where $\tau_h \in [0.9, 0.999]$ is the homeostatic time constant. The deviation from set-point is:

$$\delta_t = \|\phi_t - \bar{\phi}_t\|_2$$

The adaptation rate $\eta_t$ is modulated based on BOCPD detection and homeostatic deviation:

$$\eta_t = \eta_{\text{base}} \cdot \begin{cases} \gamma_{\text{stable}} & \text{if no drift detected and } \delta_t < \delta_{\text{thresh}} \\ \gamma_{\text{plastic}} & \text{if drift detected} \\ \gamma_{\text{restore}} \cdot (1 + \delta_t / \delta_{\text{thresh}}) & \text{otherwise} \end{cases}$$

where $\gamma_{\text{stable}} < 1 < \gamma_{\text{restore}} < \gamma_{\text{plastic}}$ control the stability-plasticity trade-off.