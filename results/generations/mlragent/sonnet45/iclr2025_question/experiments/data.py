"""
Data generation module for creating synthetic conversational datasets
with contradictions for testing SCG framework.
"""

import json
import random
import os
from typing import List, Dict, Tuple

import config


class ConversationGenerator:
    """Generate synthetic conversations with controlled contradictions."""

    def __init__(self):
        self.domains = ["medical", "legal", "technical"]
        self.topics = {
            "medical": [
                "diabetes treatment", "heart disease prevention", "mental health",
                "nutrition advice", "exercise recommendations"
            ],
            "legal": [
                "contract law", "property rights", "employment law",
                "intellectual property", "family law"
            ],
            "technical": [
                "software architecture", "database design", "cloud computing",
                "cybersecurity", "machine learning"
            ]
        }

        # Template responses for each domain
        self.response_templates = {
            "medical": [
                "Based on current medical guidelines, {topic} typically involves {aspect}. Regular monitoring and adherence to treatment protocols are essential.",
                "For {topic}, the recommended approach includes {aspect}. This has been shown to improve outcomes in clinical studies.",
                "When addressing {topic}, healthcare providers often suggest {aspect}. Patient education and lifestyle modifications play a crucial role.",
                "Research indicates that {topic} is best managed through {aspect}. Early intervention can make a significant difference.",
                "The key to effective {topic} lies in {aspect}. Coordination with healthcare professionals is important."
            ],
            "legal": [
                "In {topic}, the primary consideration is {aspect}. Legal precedent and statutory requirements must be carefully evaluated.",
                "When dealing with {topic}, it's important to understand that {aspect}. Proper documentation is essential.",
                "The framework for {topic} involves {aspect}. Consultation with legal counsel is strongly advised.",
                "{topic} requires careful attention to {aspect}. Compliance with relevant regulations is mandatory.",
                "Legal principles governing {topic} emphasize {aspect}. Due diligence is critical in these matters."
            ],
            "technical": [
                "In {topic}, best practices recommend {aspect}. Scalability and maintainability should be considered.",
                "When implementing {topic}, developers typically use {aspect}. Performance optimization is a key factor.",
                "The architecture for {topic} should include {aspect}. Security considerations are paramount.",
                "{topic} relies on {aspect}. Regular testing and monitoring ensure reliability.",
                "Modern approaches to {topic} involve {aspect}. Documentation and code review are essential practices."
            ]
        }

        self.aspects = {
            "medical": [
                "medication management and lifestyle changes",
                "regular check-ups and preventive care",
                "evidence-based treatment protocols",
                "patient-centered care and shared decision-making",
                "holistic approaches and complementary therapies"
            ],
            "legal": [
                "thorough contract review and negotiation",
                "clear documentation and record-keeping",
                "compliance with statutory requirements",
                "risk assessment and mitigation strategies",
                "dispute resolution mechanisms"
            ],
            "technical": [
                "modular design and separation of concerns",
                "automated testing and continuous integration",
                "scalable infrastructure and load balancing",
                "security best practices and encryption",
                "version control and code review processes"
            ]
        }

    def generate_base_conversation(self, domain: str, num_turns: int) -> List[Dict]:
        """Generate a base conversation without contradictions."""
        topic = random.choice(self.topics[domain])

        conversation = []

        # Initial user query
        initial_query = self._generate_initial_query(domain, topic)
        conversation.append({
            "turn": 0,
            "speaker": "user",
            "text": initial_query
        })

        # Generate consistent responses
        for turn in range(1, num_turns + 1):
            if turn % 2 == 1:  # AI response
                response = self._generate_ai_response(domain, topic)
                conversation.append({
                    "turn": turn,
                    "speaker": "assistant",
                    "text": response
                })
            else:  # User follow-up
                follow_up = self._generate_user_followup()
                conversation.append({
                    "turn": turn,
                    "speaker": "user",
                    "text": follow_up
                })

        return conversation

    def _generate_initial_query(self, domain: str, topic: str) -> str:
        """Generate an initial user query."""
        templates = {
            "medical": f"Can you explain about {topic}?",
            "legal": f"What should I know about {topic}?",
            "technical": f"How does {topic} work?"
        }
        return templates.get(domain, f"Tell me about {topic}")

    def _generate_ai_response(self, domain: str, topic: str) -> str:
        """Generate AI response using templates."""
        template = random.choice(self.response_templates[domain])
        aspect = random.choice(self.aspects[domain])
        response = template.format(topic=topic, aspect=aspect)
        return response

    def _generate_user_followup(self) -> str:
        """Generate a user follow-up question."""
        questions = [
            "Can you elaborate on that?",
            "What about specific examples?",
            "Are there any exceptions to this?",
            "How does this apply in practice?",
            "What are the main considerations?"
        ]
        return random.choice(questions)

    def inject_contradiction(self, conversation: List[Dict],
                           turn_distance: int) -> Tuple[List[Dict], Dict]:
        """Inject a contradiction at a specific temporal distance."""
        # Find assistant responses
        assistant_turns = [i for i, msg in enumerate(conversation)
                          if msg["speaker"] == "assistant"]

        if len(assistant_turns) < 2:
            return conversation, {}

        # Adjust turn_distance if needed
        max_distance = len(assistant_turns) - 1
        if turn_distance >= max_distance:
            turn_distance = max(1, max_distance // 2)

        # Select source and target turns for contradiction
        source_candidates = assistant_turns[:-turn_distance] if len(assistant_turns) > turn_distance else assistant_turns[:-1]
        if not source_candidates:
            return conversation, {}

        source_idx = random.choice(source_candidates)
        possible_targets = [t for t in assistant_turns
                          if t > source_idx + turn_distance]

        if not possible_targets:
            return conversation, {}

        target_idx = random.choice(possible_targets)

        # Extract original claim
        original_text = conversation[source_idx]["text"]

        # Generate contradictory statement
        contradictory_text = self._generate_contradiction(original_text)

        # Replace target response with contradiction
        conversation[target_idx]["text"] = contradictory_text
        conversation[target_idx]["is_contradiction"] = True
        conversation[target_idx]["contradicts_turn"] = source_idx

        annotation = {
            "has_contradiction": True,
            "source_turn": source_idx,
            "target_turn": target_idx,
            "temporal_distance": target_idx - source_idx,
            "original_claim": original_text,
            "contradictory_claim": contradictory_text
        }

        return conversation, annotation

    def _generate_contradiction(self, original_text: str) -> str:
        """Generate a contradictory version of the original text."""
        # Simple rule-based contradiction generation
        contradictions = {
            "typically involves": "does not involve",
            "recommended approach includes": "recommended approach excludes",
            "best managed through": "should avoid",
            "essential": "not necessary",
            "important": "not important",
            "should include": "should not include",
            "requires": "does not require",
            "emphasize": "de-emphasize",
            "recommend": "discourage",
            "effective": "ineffective",
            "beneficial": "harmful",
            "improve": "worsen",
            "increase": "decrease",
            "positive": "negative",
            "advisable": "inadvisable"
        }

        contradictory_text = original_text
        for original, replacement in contradictions.items():
            if original in contradictory_text.lower():
                # Case-insensitive replacement
                import re
                pattern = re.compile(re.escape(original), re.IGNORECASE)
                contradictory_text = pattern.sub(replacement, contradictory_text, count=1)
                break

        # If no direct contradiction found, add negation
        if contradictory_text == original_text:
            contradictory_text = "However, recent findings suggest the opposite. " + contradictory_text.replace(
                "The", "Actually, the").replace("is", "is not").replace("should", "should not")

        return contradictory_text

    def generate_dataset(self, num_conversations: int) -> List[Dict]:
        """Generate complete dataset with conversations."""
        dataset = []

        for i in range(num_conversations):
            domain = random.choice(self.domains)
            num_turns = random.randint(*config.NUM_TURNS_RANGE)

            # Generate base conversation
            conversation = self.generate_base_conversation(domain, num_turns)

            # Decide whether to inject contradiction (50% chance)
            if random.random() < 0.5:
                turn_distance = random.randint(*config.CONTRADICTION_DISTANCE_RANGE)
                conversation, annotation = self.inject_contradiction(
                    conversation, turn_distance
                )
            else:
                annotation = {"has_contradiction": False}

            dataset.append({
                "conversation_id": i,
                "domain": domain,
                "conversation": conversation,
                "annotation": annotation
            })

            if (i + 1) % 10 == 0:
                print(f"Generated {i + 1}/{num_conversations} conversations")

        return dataset


def save_dataset(dataset: List[Dict], filename: str):
    """Save dataset to JSON file."""
    os.makedirs(config.DATA_DIR, exist_ok=True)
    filepath = os.path.join(config.DATA_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(dataset, f, indent=2)
    print(f"Dataset saved to {filepath}")


def load_dataset(filename: str) -> List[Dict]:
    """Load dataset from JSON file."""
    filepath = os.path.join(config.DATA_DIR, filename)
    with open(filepath, 'r') as f:
        dataset = json.load(f)
    return dataset


if __name__ == "__main__":
    # Generate synthetic dataset
    print("Generating synthetic conversational dataset...")
    generator = ConversationGenerator()
    dataset = generator.generate_dataset(config.NUM_SYNTHETIC_CONVERSATIONS)
    save_dataset(dataset, "synthetic_conversations.json")

    # Print statistics
    with_contradictions = sum(1 for d in dataset if d["annotation"]["has_contradiction"])
    print(f"\nDataset statistics:")
    print(f"Total conversations: {len(dataset)}")
    print(f"With contradictions: {with_contradictions}")
    print(f"Without contradictions: {len(dataset) - with_contradictions}")
