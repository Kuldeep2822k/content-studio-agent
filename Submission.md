# Kaggle Capstone Submission – Content Studio Agent (Freestyle Track)

## 1. Project Title

**Content Studio Agent – Research, Outline, and Draft Assistant**

## 2. Problem & Motivation

Writing high-quality technical and educational content is time-consuming. You have to research a topic across multiple sources, organize ideas into a clear structure, and then draft the full article. This makes it hard for individual creators and small teams to publish consistently at a high quality. Existing tools often focus on only one part of the workflow (e.g., grammar checking or paraphrasing) instead of supporting the end-to-end process from research to evaluation.

## 3. Solution Overview

The **Content Studio Agent** is an AI writing assistant that turns a topic and target audience into a researched outline and first draft, then evaluates the draft automatically.

The agent orchestrates four main stages:

1. **Research** – Calls a web search tool (backed by SerpAPI) to gather background information and recent context about the topic.
2. **Outline** – Uses Gemini to transform research notes into a structured, markdown-style outline tailored to the specified audience, tone, and length.
3. **Draft** – Expands the outline into a full article draft, taking into account stored user style preferences.
4. **Evaluation** – Uses an LLM-as-judge style evaluator agent to score the draft on:
   - Relevance to the topic
   - Structure and clarity
   - Style and tone alignment

The agent stores each run’s data in session memory and updates long-term user style preferences so future drafts are better aligned with the same voice.

The full source code is available at: `https://github.com/<your-username>/content-studio-agent`.

## 4. How It Uses the Course Concepts

### Unit 1 – Introduction to Agents

- Implements a single orchestrator agent (`ContentStudioAgent`) that handles the end-to-end workflow of research → outline → draft → evaluation.
- The orchestration logic is explicit in Python, making the agent’s decision-making traceable and easy to inspect.

### Unit 2 – Agent Tools & Interoperability

- Defines a **web search tool** in `tools/web_search_tool.py` that uses SerpAPI’s Google Search API to fetch live web results.
- The tool returns normalized `{title, url, snippet}` dictionaries that the agent consumes when building outlines and drafts.
- The web search tool is independent of the core agent logic, demonstrating clean separation between tools and orchestration. It can be swapped for another provider (e.g., MCP-based tool, Google Programmable Search Engine) without changing the agent itself.

### Unit 3 – Context Engineering: Sessions & Memory

- **Session memory** (`memory/session_memory.py`):
  - Stores per-session events (topic, outline, draft, evaluation) as JSON files under `data/sessions/`.
  - Provides a simple way to inspect the agent’s past runs and conversation history at the session level.
- **Long-term memory / user profile** (`memory/user_profile_store.py`):
  - Stores user style preferences under `data/users/{user_id}.json`.
  - The agent reads these preferences on each run (e.g., default tone) and updates them when the user chooses a new style, enabling personalization across sessions.

### Unit 4 – Agent Quality

- **Observability**:
  - Uses Python `logging` to record key events, including when the agent starts research, builds an outline, generates a draft, and runs evaluation.
  - Session JSON files serve as simple traces that show how the agent responded in specific scenarios.
- **Evaluation (LLM-as-judge)**:
  - The `EvaluatorAgent` in `eval/evaluator_agent.py` prompts Gemini to score drafts on:
    - `relevance_to_topic`
    - `structure_and_clarity`
    - `style_and_tone_alignment`
  - The evaluator is instructed to return JSON so the scores and comments can be captured programmatically and compared across runs.

### Unit 5 – Prototype to Production

- **Prototype**:
  - `demo.py` provides an interactive CLI experience where the user enters a topic, audience, tone, and length, and receives an outline, draft, and evaluation.
- **API / Service**:
  - `api/main.py` exposes the agent as a FastAPI service with a `POST /create_article` endpoint.
  - This endpoint takes the same inputs as the CLI and returns a structured JSON response suitable for integration into other systems (e.g., a web UI or another agent).
- **Production Considerations**:
  - The agent logic and FastAPI layer can be containerized and deployed as a microservice, or integrated into Vertex AI Agent Engine as the "writer" component in a larger multi-agent workflow (e.g., researcher → planner → writer → reviewer).

## 5. Implementation Details

- **Language & Frameworks**: Python, FastAPI
- **Models**: Gemini (via `google-generativeai`)
- **Tools**:
  - Web search using SerpAPI’s Google Search API (HTTP via `requests`).
- **Memory**:
  - JSON-file-backed session memory and user profile store.
- **Evaluation**:
  - Custom evaluator agent prompting Gemini to score drafts and return JSON.

The repository is organized as follows:

- `agents/content_agent.py` – main `ContentStudioAgent` implementation.
- `tools/web_search_tool.py` – web search tool using SerpAPI.
- `memory/session_memory.py` – per-session event storage.
- `memory/user_profile_store.py` – long-term user style preferences.
- `eval/evaluator_agent.py` – LLM-as-judge evaluator.
- `api/main.py` – FastAPI app exposing the agent over HTTP.
- `demo.py` – CLI demo script.

## 6. Evaluation & Results

To evaluate the agent, I defined a small set of example topics such as:

1. "Introduction to AI Agents for Beginners"
2. "Best Practices for Prompt Engineering"
3. "How Context Windows and Memory Work in LLM Agents"

For each topic, I ran the agent end-to-end and collected:

- The generated outline
- The article draft
- The evaluator’s JSON scores and comments

The evaluator scores provided a quick way to compare runs. For example, drafts that followed the outline closely and had clear section structure received higher `structure_and_clarity` scores. When I intentionally changed the tone or audience, the `style_and_tone_alignment` score reflected whether the agent adapted appropriately.

In the writeup, I highlight:

- Where the agent performed well (e.g., strong structure and clear introductions).
- Areas for improvement (e.g., occasionally repetitive conclusions or shallow treatment of complex topics).

## 7. Impact & Future Work

**Impact:**

- For solo creators or small teams, the Content Studio Agent reduces the time required to go from topic idea to first draft, while still keeping the user in control of the final editing and fact-checking.
- The project demonstrates how agent concepts from the course (tools, memory, evaluation, and deployment) can be combined into a practical end-to-end workflow.

**Future work:**

- Split the single agent into a **multi-agent system** (researcher, planner, writer, evaluator) using patterns from the course.
- Replace JSON-file memory with a database or vector store for more scalable and semantically rich memory.
- Add a review agent that automatically suggests edits or alternative phrasings for low-scoring sections.
- Connect the FastAPI service to a front-end UI (e.g., Streamlit or a custom web app) for non-technical users.

## 8. Optional Video Script (3–5 Minutes)

You can use the following script as a guide for your video submission:

1. **Intro (30–45s)**
   - "Hi, I’m <your name>, and this is my Freestyle track capstone for the 5-Day AI Agents Intensive with Google. My project is called the Content Studio Agent, an AI assistant that helps creators go from a topic idea to a researched outline, draft, and evaluation."

2. **Problem (30s)**
   - "Writing high-quality content takes time. You need to research, structure your ideas, and write a draft, which can be overwhelming if you want to publish regularly. Existing tools often focus on grammar or paraphrasing, but they don’t support the full workflow."

3. **Solution & Demo (1.5–2 min)**
   - Show the CLI or API in action:
     - Enter a topic, audience, tone, and length in the CLI (`python demo.py`) or call the FastAPI endpoint.
     - Scroll through the generated outline and draft.
     - Show the evaluation JSON and briefly explain what the scores mean.
   - Narrate: "Behind the scenes, the agent uses a web search tool backed by SerpAPI to gather context, then uses Gemini to create an outline and expand it into a draft. It also remembers my style preferences, like tone, across runs."

4. **Architecture & Course Concepts (1–1.5 min)**
   - Show the repo structure briefly and explain:
     - "There is a single `ContentStudioAgent` orchestrator and a separate web search tool in `tools/web_search_tool.py`."
     - "Session memory and user profiles are stored as JSON files to demonstrate context engineering and long-term memory."
     - "An evaluator agent implements LLM-as-judge to score drafts on relevance, structure, and style alignment."
     - "Finally, I expose the agent as a FastAPI service, which is a step towards production deployment (and could be integrated into Vertex AI Agent Engine)."

5. **Results & Future Work (30–45s)**
   - "In testing with several topics, the agent produces well-structured outlines and reasonable drafts that I can refine into final articles. The evaluation scores help me quickly identify drafts that may need more work."
   - "In the future, I’d like to split this into a multi-agent system (researcher, planner, writer, reviewer) and add a UI on top of the FastAPI service."

6. **Closing (10–20s)**
   - "Thanks for watching my Content Studio Agent demo, and thanks to the Google and Kaggle teams for the 5-Day AI Agents Intensive."
