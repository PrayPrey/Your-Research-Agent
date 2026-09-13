# Related Work

## Neural Network Calibration

Temperature scaling emerged as the dominant post-hoc calibration method after Guo et al. \cite{guo2017calibration} demonstrated that modern neural networks are poorly calibrated despite high accuracy. Their work established Expected Calibration Error (ECE) as the standard metric and showed that a single learned temperature parameter substantially reduces miscalibration. Subsequent work extended calibration to structured prediction \cite{kuleshov2018accurate}, regression \cite{song2019distribution}, and multi-class settings. Class-based temperature scaling \cite{frenkel2021class} showed that per-class temperatures can outperform global scaling in vision tasks — a direct inspiration for our category-specific approach.

## LLM Uncertainty Quantification

Recent work has examined uncertainty in large language models. Kadavath et al. \cite{kadavath2022language} studied "self-knowledge" — whether models can identify questions they cannot answer correctly. Xiong et al. \cite{xiong2023uncertainty} compared verbalized confidence (asking models to state uncertainty as percentages) against logit-based probabilities, finding that different elicitation methods yield different calibration properties. APRICOT \cite{arteaga2024apricot} demonstrated that calibration is possible even for generation tasks without logit access. Thermometer \cite{mao2024thermometer} proposed universal calibration across tasks via learned embeddings.

A key finding across this literature: LLMs trained with RLHF exhibit systematic overconfidence \cite{xiong2023uncertainty}. This overconfidence manifests as high confidence on incorrect answers, suggesting the reward model encourages confident-sounding responses regardless of accuracy.

## Truthfulness Benchmarks

TruthfulQA \cite{lin2022truthfulqa} provides the primary benchmark for our work. It contains 817 questions across 38 categories designed to elicit false statements that humans find plausible. Categories span domains from scientific misconceptions to legal and political claims. The benchmark evaluates both truthfulness (is the answer factually correct?) and informativeness (does the answer actually address the question?). 

FACTOR \cite{factor2023} offers a complementary factuality benchmark with longer-form claims. While our primary experiments use TruthfulQA for its category structure, FACTOR provides a potential transfer validation target.

## The Gap We Address

No prior work has disaggregated calibration metrics by category on TruthfulQA. Existing calibration studies compute global ECE across entire datasets. TruthfulQA analyses focus on truthfulness accuracy, not calibration error patterns. This leaves a fundamental question unanswered: does the semantic category of a factual claim predict how (mis)calibrated the model will be?

Class-based temperature scaling \cite{frenkel2021class} showed category-specific calibration helps in vision. But applying this insight to LLMs faces a key challenge: if RLHF induces *uniform* overconfidence, category structure may not provide useful calibration signal. Our work directly tests this question.
