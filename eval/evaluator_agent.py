import logging
from typing import Dict, Any, List

from config import get_gemini_model

logger = logging.getLogger(__name__)


class EvaluatorAgent:
    """LLM-as-judge style evaluator for article drafts."""

    def __init__(self, model_name: str = "gemini-2.0-flash", api_key_env: str = "GEMINI_API_KEY") -> None:
        self.model = get_gemini_model(model_name=model_name, api_key_env=api_key_env)

    def evaluate_draft(
        self,
        topic: str,
        outline: str,
        draft: str,
        research_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        logger.info("Evaluating draft", extra={"topic": topic})

        prompt = (
            "You are evaluating an article draft. Score each criterion from 1-5 and provide a short justification.\n" \
            "Criteria: relevance_to_topic, structure_and_clarity, style_and_tone_alignment.\n" \
            "Return JSON with fields: {""relevance_to_topic"": int, ""structure_and_clarity"": int, ""style_and_tone_alignment"": int, ""comments"": string}.\n\n" \
            f"Topic: {topic}\n\n" \
            "Outline:\n" + outline + "\n\n" \
            "Draft:\n" + draft + "\n\n" \
            "Research notes (for factual grounding):\n"
        )

        for item in research_results:
            prompt += f"- {item.get('title', '')}: {item.get('snippet', '')}\n"

        resp = self.model.generate_content([
            "You must respond with valid JSON only, no additional text.",
            prompt,
        ])

        # The API returns text; we parse it defensively.
        import json

        try:
            data = json.loads(resp.text)
        except json.JSONDecodeError:
            logger.warning("Evaluator returned non-JSON, wrapping in fallback", extra={"raw": resp.text})
            data = {
                "relevance_to_topic": None,
                "structure_and_clarity": None,
                "style_and_tone_alignment": None,
                "comments": resp.text,
            }

        return data
