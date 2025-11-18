import json
import logging
import os
import uuid

try:
    from agents.content_agent import ContentStudioAgent
    AGENT_AVAILABLE = True
except Exception as e:
    AGENT_AVAILABLE = False
    AGENT_ERROR = str(e)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def demo_output(topic: str, audience: str, tone: str, length: str) -> dict:
    """Generate demo output when the agent is unavailable."""
    return {
        "outline": f"""## Introduction to {topic}
### What is {topic}?
### Why Learn {topic}?

## Core Concepts
### Concept 1
### Concept 2

## Getting Started
### First Steps
### Best Practices

## Conclusion""",
        "draft": f"""# {topic} for {audience.capitalize()}s

This article explores the fundamentals of {topic}.

## Introduction to {topic}

{topic} is an important concept in modern technology. Whether you're just starting out or looking to deepen your understanding, this guide will walk you through the essentials.

## Core Concepts

There are several fundamental concepts to understand:

1. **Concept 1**: First core principle
2. **Concept 2**: Second core principle

## Getting Started

To begin with {topic}, follow these steps:

1. Understand the basics
2. Explore practical examples
3. Practice with real scenarios

## Conclusion

{topic} is a growing field with many opportunities. By mastering these fundamentals, you'll be well-equipped to explore this area further.""",
        "evaluation": {
            "relevance_to_topic": 4,
            "structure_and_clarity": 4,
            "style_and_tone_alignment": 4,
            "comments": "Demo output generated. Outline and draft follow the intended structure with appropriate tone for a beginner audience."
        },
        "research_results": [
            {"title": f"Background on {topic}", "url": "https://example.com", "snippet": "Key information about the topic"}
        ]
    }


def main() -> None:
    if "GEMINI_API_KEY" not in os.environ:
        print("Note: GEMINI_API_KEY not found. Running in demo mode.\n")

    topic = input("Enter a topic for your article: ").strip()
    if not topic:
        print("Error: Topic cannot be empty.")
        return
    
    audience = input("Target audience (e.g., beginners, developers, managers): ").strip()
    if not audience:
        audience = "general"
    
    tone = input("Tone (e.g., friendly, professional): ").strip()
    if not tone:
        tone = "friendly"
    
    length = input("Length (short, medium, long): ").strip()
    if not length:
        length = "medium"

    session_id = str(uuid.uuid4())
    user_id = "demo-user"

    if AGENT_AVAILABLE:
        try:
            agent = ContentStudioAgent()
            result = agent.create_article(
                session_id=session_id,
                user_id=user_id,
                topic=topic,
                audience=audience,
                tone=tone,
                length=length,
            )
        except Exception as e:
            print(f"\n⚠️  Agent encountered an error (likely API key restrictions): {str(e)[:200]}\n")
            print("Generating demo output instead...\n")
            result = demo_output(topic, audience, tone, length)
    else:
        print(f"\n⚠️  Could not load agent: {AGENT_ERROR}\n")
        print("Generating demo output instead...\n")
        result = demo_output(topic, audience, tone, length)

    print("\n=== OUTLINE ===\n")
    print(result["outline"])

    print("\n=== DRAFT ===\n")
    print(result["draft"])

    print("\n=== EVALUATION ===\n")
    print(json.dumps(result["evaluation"], indent=2))


if __name__ == "__main__":
    main()
