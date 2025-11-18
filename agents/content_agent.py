import logging
from typing import Dict, Any, List

from memory.session_memory import SessionMemory
from memory.user_profile_store import UserProfileStore
from eval.evaluator_agent import EvaluatorAgent
from config import get_gemini_model


logger = logging.getLogger(__name__)


class ContentStudioAgent:
    """Single-agent orchestrator for research → outline → draft → evaluation.

    This implementation keeps orchestration explicit instead of relying on
    automatic tool-calling so it is easy to debug and reason about for the
    capstone writeup.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash",
        api_key_env: str = "GEMINI_API_KEY",
        session_store: SessionMemory | None = None,
        profile_store: UserProfileStore | None = None,
        evaluator: EvaluatorAgent | None = None,
    ) -> None:
        # Configure Gemini model via shared config helper (loads env/.env).
        self.model = get_gemini_model(model_name=model_name, api_key_env=api_key_env)

        self.session_store = session_store or SessionMemory()
        self.profile_store = profile_store or UserProfileStore()
        self.evaluator = evaluator or EvaluatorAgent(model_name=model_name)

    # ---------- public API ----------

    def create_article(
        self,
        session_id: str,
        user_id: str,
        topic: str,
        audience: str = "general",
        tone: str = "friendly",
        length: str = "medium",
        constraints: str | None = None,
    ) -> Dict[str, Any]:
        """Main entry point: returns outline, draft, and evaluation.

        Results are also logged into session memory.
        """
        logger.info("create_article called", extra={"topic": topic, "audience": audience})

        user_profile = self.profile_store.load_profile(user_id)
        style_prefs = user_profile.get("style", {})

        # 1) Research
        research_results = self._research(topic)

        # 2) Outline
        outline = self._create_outline(
            topic=topic,
            audience=audience,
            tone=tone,
            length=length,
            constraints=constraints,
            research_results=research_results,
            style_prefs=style_prefs,
        )

        # 3) Draft
        draft = self._create_draft(
            topic=topic,
            outline=outline,
            audience=audience,
            tone=tone,
            length=length,
            style_prefs=style_prefs,
        )

        # 4) Evaluation (LLM-as-judge)
        evaluation = self.evaluator.evaluate_draft(
            topic=topic,
            outline=outline,
            draft=draft,
            research_results=research_results,
        )

        # 5) Persist session + profile updates
        self.session_store.append_event(
            session_id=session_id,
            event={
                "type": "article_run",
                "topic": topic,
                "audience": audience,
                "tone": tone,
                "length": length,
                "constraints": constraints,
                "outline": outline,
                "draft": draft,
                "evaluation": evaluation,
            },
        )

        # Simple example of updating user preferences based on tone choice
        self.profile_store.update_style_preferences(user_id, {"tone": tone})

        return {
            "outline": outline,
            "draft": draft,
            "evaluation": evaluation,
            "research_results": research_results,
        }

    # ---------- internal steps ----------

    def _research(self, topic: str) -> List[Dict[str, Any]]:
        logger.info("Starting research", extra={"topic": topic})
        # Generate research summary directly using Gemini instead of web search
        prompt = f"Provide 3-4 key facts or points about {topic} in bullet format. Be concise."
        resp = self.model.generate_content(prompt)
        # Parse the response into structured format
        return [
            {"title": f"Key information about {topic}", "snippet": resp.text, "url": ""}
        ]

    def _create_outline(
        self,
        topic: str,
        audience: str,
        tone: str,
        length: str,
        constraints: str | None,
        research_results: List[Dict[str, Any]],
        style_prefs: Dict[str, Any],
    ) -> str:
        logger.info("Creating outline", extra={"topic": topic})
        prompt = (
            "You are a content strategist helping plan an article.\n" \
            "Use the research notes below to propose a structured outline.\n" \
            "Return markdown headings only (H2/H3).\n\n" \
            f"Topic: {topic}\n" \
            f"Target audience: {audience}\n" \
            f"Tone: {tone}\n" \
            f"Desired length: {length}\n" \
        )
        if constraints:
            prompt += f"Constraints: {constraints}\n"
        if style_prefs:
            prompt += f"User style preferences: {style_prefs}\n"

        prompt += "\nResearch notes:\n"
        for item in research_results:
            prompt += f"- {item.get('title', '')}: {item.get('snippet', '')}\n"

        resp = self.model.generate_content(prompt)
        return resp.text

    def _create_draft(
        self,
        topic: str,
        outline: str,
        audience: str,
        tone: str,
        length: str,
        style_prefs: Dict[str, Any],
    ) -> str:
        logger.info("Creating draft", extra={"topic": topic})
        prompt = (
            "You are a professional writer. Write a full article based on the outline.\n" \
            "Follow the headings and keep the structure clear.\n\n" \
            f"Topic: {topic}\n" \
            f"Target audience: {audience}\n" \
            f"Tone: {tone}\n" \
            f"Desired length: {length}\n" \
        )
        if style_prefs:
            prompt += f"User style preferences: {style_prefs}\n"

        prompt += "\nOutline:\n" + outline

        resp = self.model.generate_content(prompt)
        return resp.text
