from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from .config import OLLAMA_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL
from .models import Series


class SummaryResult(BaseModel):
    summary: str
    highlights: list[str]


def _build_agent() -> Agent[str]:
    model = OpenAIModel(
        model_name=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        api_key=OLLAMA_API_KEY,
    )
    return Agent(
        model,
        system_prompt=(
            "You summarize a TV series catalog for a casual viewer. "
            "Return plain text in this exact format:\n"
            "Summary: <one short paragraph>\n"
            "Highlights:\n"
            "- <bullet>\n"
            "- <bullet>\n"
            "- <bullet>"
        ),
    )


async def generate_summary(series: list[Series]) -> SummaryResult:
    if not series:
        return SummaryResult(
            summary="No series yet. Add a few entries to generate insights.",
            highlights=[],
        )
    lines = [
        f"{row.title} ({row.year}) by {row.creator} rating {row.rating}"
        if row.rating is not None
        else f"{row.title} ({row.year}) by {row.creator} rating n/a"
        for row in series
    ]
    prompt = "Catalog:\n" + "\n".join(lines)
    agent = _build_agent()
    try:
        result = await agent.run(prompt)
        text = result.data.strip()
        summary = ""
        highlights: list[str] = []
        if "Summary:" in text:
            parts = text.split("Summary:", 1)[1].split("Highlights:", 1)
            summary = parts[0].strip().strip("-").strip()
            if len(parts) > 1:
                highlights_block = parts[1]
                for line in highlights_block.splitlines():
                    line = line.strip()
                    if line.startswith("-"):
                        highlights.append(line.lstrip("-").strip())
        if not summary:
            summary = text.splitlines()[0].strip() if text else "Summary unavailable."
        return SummaryResult(summary=summary, highlights=highlights)
    except Exception:
        return SummaryResult(
            summary="AI summary unavailable (model response was invalid).",
            highlights=[],
        )
