from __future__ import annotations

import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from agents.content_agent import ContentStudioAgent


app = FastAPI(title="Content Studio Agent API", version="1.0.0")

agent = ContentStudioAgent()


class ArticleRequest(BaseModel):
    session_id: str | None = None
    user_id: str = "api-user"
    topic: str
    audience: str = "general"
    tone: str = "friendly"
    length: str = "medium"
    constraints: str | None = None


class ArticleResponse(BaseModel):
    outline: str
    draft: str
    evaluation: dict
    research_results: list


@app.get("/")
async def root() -> dict:
    return {"message": "Content Studio Agent API is running"}


@app.post("/create_article", response_model=ArticleResponse)
async def create_article(req: ArticleRequest) -> ArticleResponse:
    session_id = req.session_id or str(uuid.uuid4())

    result = agent.create_article(
        session_id=session_id,
        user_id=req.user_id,
        topic=req.topic,
        audience=req.audience,
        tone=req.tone,
        length=req.length,
        constraints=req.constraints,
    )

    return ArticleResponse(
        outline=result["outline"],
        draft=result["draft"],
        evaluation=result["evaluation"],
        research_results=result["research_results"],
    )
