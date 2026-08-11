"""
Step 3: BRAND. Turns a ContentPack's logo_prompt into a logo image.

Owned by Station 1. There is no real implementation yet, mock or otherwise —
image generation is expensive (shared MAX_IMAGE_CALLS cap) and not needed
for today's demo, so this always returns None regardless of settings.MOCK.
A None return is a normal, expected outcome: app/main.py's background task
treats it as "logo_status": "failed", which is honest (no attempt was made).
"""

from app.models import ContentPack


async def generate_logo(pack: ContentPack) -> bytes | None:
    # Station 1 TODO: call gpt-image-1 here (see 01_STATION_1 task T4); must
    # check config.can_call_image() before calling and never raise — return
    # None on any failure or cap.
    return None
