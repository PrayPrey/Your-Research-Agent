# Title
Adaptive Pedagogical Prompting: Training LLMs to Scaffold Learning Through Socratic Dialogue

# Motivation
Current generative AI tutors often provide direct answers, undermining learning-by-doing principles. Research shows that effective tutoring involves strategic questioning and scaffolding rather than solution-giving. However, standard LLMs lack pedagogical awareness about when to reveal information versus prompt deeper thinking. This creates a critical gap between AI capabilities and sound educational practice, potentially fostering learned helplessness rather than independent problem-solving skills.

# Main Idea
Develop a fine-tuning framework that trains LLMs to employ pedagogically-sound Socratic questioning strategies. The methodology involves:

1. **Curriculum Design**: Create a dataset of expert tutor-student interactions annotated with pedagogical strategies (hint levels, misconception addressing, metacognitive prompts).

2. **Adaptive Scaffolding Model**: Fine-tune LLMs using reinforcement learning from human feedback (RLHF) where rewards are based on: (a) student learning gains rather than satisfaction, (b) maintaining productive struggle duration, and (c) fostering self-explanation.

3. **Context-Aware Prompting**: Implement a dynamic prompting system that adjusts intervention levels based on student affect, attempt history, and knowledge state inferred from dialogue.

**Expected Outcomes**: An AI tutor that balances support with challenge, promotes deeper learning, and can be validated through A/B testing measuring learning gains and transfer. This addresses both GAI→ED (enhancing tutoring systems) and ED→GAI (safeguarding against over-reliance on AI).