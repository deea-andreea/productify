from app.models import ContentPack, Tone, VisionResult

# Owned by the Station 1 NAVIGATOR. Four genuinely different registers, not four
# intensities of the same voice. Filled in during T1/T2.
TONE_BRIEFS: dict[Tone, str] = {
    Tone.vc: "TODO",
    Tone.luxury: "TODO",
    Tone.infomercial: "TODO",
    Tone.kickstarter: "TODO",
}


def build_vision_prompt() -> str:
    return "TODO"


def build_content_prompt(vision: VisionResult, tone: Tone) -> str:
    return "TODO"


def build_logo_prompt(pack: ContentPack) -> str:
    return "TODO"
