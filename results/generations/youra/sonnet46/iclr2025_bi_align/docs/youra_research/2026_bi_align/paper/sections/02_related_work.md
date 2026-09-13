# Related Work

Our work sits at the intersection of communication accommodation theory, RLHF alignment evaluation, human-AI interaction research, and semantic similarity measurement. We review each area and highlight why existing work is insufficient to explain the phenomenon we measure.

## 2.1 Communication Accommodation Theory and Linguistic Coordination

Communication Accommodation Theory (CAT) [Giles, 1973; Giles & Ogay, 2007] posits that interlocutors converge or diverge linguistically based on social, relational, and cognitive factors. Lower-power interlocutors tend to accommodate more to higher-power ones — a prediction supported empirically in human-human settings. Danescu-Niculescu-Mizil et al. [2012] operationalized this as linguistic coordination (C_m) using function-word category frequencies in Wikipedia administrator discussions and U.S. Supreme Court oral arguments, demonstrating that language users accommodate to partners who hold authority over them. Their measure captures surface-level lexical accommodation in closed-class word categories.

Our work extends this framework in two directions. First, we move from function-word coordination (lexical/syntactic level) to semantic embedding space (SBERT cosine similarity), capturing richer meaning-level alignment between interlocutors. Second, we apply this framework to human-AI conversations with a structured quality gradient (RLHF tiers) as the power/authority variable, rather than institutional role. The C_sem metric we introduce is conceptually analogous to C_m but operates in a continuous semantic space, enabling measurement of accommodation patterns that lexical coordination misses.

Several studies have examined linguistic alignment in human-human conversation using distributional semantic methods [Fusaroli et al., 2012; Pickering & Garrod, 2004], and more recently in human-computer interaction [Porcheron et al., 2018]. However, none have examined SBERT-based semantic accommodation across RLHF alignment tiers, leaving the quality-accommodation relationship in AI conversation entirely unmeasured.

## 2.2 RLHF Alignment and Human Preference Learning

RLHF [Christiano et al., 2017; Ouyang et al., 2022] has become the dominant technique for aligning language model outputs with human preferences. Bai et al. [2022] introduced the HH-RLHF dataset comprising three helpfulness tiers (helpful-base, helpful-rejection-sampling, helpful-online), each representing a higher stage of RLHF quality optimization: base supervised fine-tuning, rejection-sampling with reward model filtering, and online PPO-based fine-tuning. This tier structure encodes a principled AI quality gradient.

Existing RLHF evaluation research uses the tier structure to measure *AI* output quality — response helpfulness, harmlessness, and instruction-following [Bai et al., 2022; Ouyang et al., 2022; Stiennon et al., 2020]. Our work inverts this paradigm: we treat RLHF tier as the independent variable and measure human conversational behavior as the dependent variable. To our knowledge, no prior work has used HH-RLHF tier structure to study how RLHF quality shapes downstream human semantic patterns. This reframing is our core methodological departure from prior alignment evaluation.

## 2.3 Human-AI Style Adaptation and Bidirectional Alignment

Recent work has begun examining how humans adapt to AI conversational style. Chang & Wang [2025] demonstrated word-level bidirectional style adaptation in human-AI conversations across cultural contexts — humans adjust their lexical style when interacting with AI, and AI systems (when designed to do so) reciprocate. However, their work operates at the word-level style matching layer and does not examine the role of RLHF alignment quality as a driver of accommodation strength.

The BiAlign framework [Shen et al., 2025] motivates the study of bidirectional alignment — recognizing that human-AI conversations are mutual adaptation systems, not one-way quality filtering problems. However, Shen et al.'s contribution is primarily conceptual and design-focused, lacking empirical measurement of the human-side semantic adaptation component at the scale and granularity we provide.

Our work provides the missing empirical foundation: SBERT-based measurement of human semantic accommodation across RLHF quality tiers at population scale (n = 155,362 pairs), connecting the bidirectional alignment framework to reproducible quantitative measurements.

## 2.4 Semantic Similarity and Sentence Embeddings

Reimers & Gurevych [2019] introduced Sentence-BERT (SBERT), a siamese BERT architecture producing semantically meaningful sentence embeddings via mean pooling. SBERT models achieve state-of-the-art performance on semantic textual similarity benchmarks and produce embeddings where cosine similarity is a reliable measure of semantic alignment. The all-MiniLM-L6-v2 variant achieves ~14,000 sentences/second on CPU, enabling large-scale analysis without GPU training requirements.

SBERT embeddings capture both content (topical similarity) and style (semantic register, phrasing) in a unified continuous space. This is simultaneously a strength (richer than lexical coordination) and a limitation (topical and stylistic signals are entangled). We address this entanglement explicitly through our three-level partner-specificity control hierarchy: cosine similarity to the actual AI partner minus a topic-matched KNN baseline (K=5) isolates interaction-specific accommodation above topical coherence — a stricter control than prior accommodation measurement using surface statistics.

## 2.5 Power Asymmetry and Social Structure in Language

The power asymmetry hypothesis [Danescu-Niculescu-Mizil et al., 2012; Giles & Ogay, 2007] predicts that lower-status interlocutors accommodate more to higher-status partners. In human-AI interaction, the "power" relationship is not institutionally defined, but RLHF alignment quality may function as a proxy for conversational authority — higher-quality AI responses are more helpful, comprehensive, and conversationally rich, potentially triggering greater accommodation from human partners analogous to lower-power linguistic deference.

Our finding that C_sem^{H←A} > C_sem^{A←H} in all 9 tier × model cells is consistent with this prediction: humans accommodate more to AI than AI to humans. However, unlike human-human power asymmetry (where power is institutionally designated), our directional asymmetry reflects the structural properties of RLHF data collection (AI responses are optimized to be helpful and thus semantically comprehensive) rather than a conscious human recognition of AI authority. The H-M3 and H-M4 mechanism falsifications support this structural rather than perceptual explanation.

## 2.6 Summary and Positioning

Taken together, existing work provides the theoretical foundation (CAT, power asymmetry) and the technical tools (SBERT, RLHF datasets) but does not combine them to study the quality-accommodation relationship in human-AI conversations. Prior accommodation studies use lexical coordination metrics; prior RLHF evaluation studies measure AI quality, not human response; prior human-AI adaptation studies do not use RLHF tier structure. Our work is the first to address all three components simultaneously — introducing C_sem as a calibrated SBERT-based accommodation measure, using RLHF tier as a quality gradient, and empirically testing both the existence and mechanism of tier-scalable semantic accommodation in human-AI helpfulness conversations.
