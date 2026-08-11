"""
Step 2: INVENT. Turns a VisionResult + Tone into a full ContentPack.

Owned by Station 1. Mock branch loads a pre-written fixture instead of
calling the model, so Station 2 (and the rest of the app) can run the full
pipeline today without OpenAI.
"""

import json
from pathlib import Path

from app.config import settings
from app.models import ContentPack, Tone, VisionResult

_REPO_ROOT = Path(__file__).resolve().parents[2]


async def generate_content(vision: VisionResult, tone: Tone) -> ContentPack:
    if settings.MOCK:
        # `vision` is intentionally ignored in mock mode — each fixture
        # already hardcodes a matching VisionResult (the same scratched red
        # stapler `analyze_image` returns).
        fixture_path = _REPO_ROOT / "fixtures" / f"stapler.{tone.value}.json"
        if not fixture_path.exists():
            raise FileNotFoundError(
                f"No mock content fixture for tone '{tone.value}' — expected {fixture_path}"
            )
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        return ContentPack.model_validate(data)
    raise NotImplementedError(
        "Station 1 TODO: one Structured Outputs call using contracts/content_pack.schema.json, "
        "plus the palette/count/highlighted-tier repair rules in contracts/handoff.md — "
        "see 01_STATION_1 task T2"
    )
