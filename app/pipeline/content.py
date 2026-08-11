from app.models import ContentPack, Tone, VisionResult


async def generate_content(vision: VisionResult, tone: Tone) -> ContentPack:
    """Implemented in T2."""
    raise NotImplementedError
