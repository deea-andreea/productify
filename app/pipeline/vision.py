"""
Step 1: LOOK. Turns a product photo into a VisionResult.

Owned by Station 1. Mock branch below is a hardcoded stand-in so the rest of
the app (content generation, rendering, gallery) can run end-to-end today
without ever calling OpenAI.
"""

from app.config import settings
from app.models import VisionResult


async def analyze_image(photo_bytes: bytes) -> VisionResult:
    if settings.MOCK:
        return VisionResult(
            object="stapler",
            quirks=[
                "a chipped corner near the base",
                "a faded coffee-ring stain on the top plate",
                "a sticker-residue ghost where a price tag used to be",
            ],
            material="red painted steel and plastic",
            condition="well-loved, three years of desk duty",
        )
    raise NotImplementedError(
        "Station 1 TODO: wire the real gpt-5-mini vision call here — see 01_STATION_1 task T1"
    )
