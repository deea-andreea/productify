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
    return (
        "You are looking at one photographed object for a startup-pitch generator. "
        "Identifying the object is the least valuable part of your answer.\n\n"
        "The most valuable part is the quirks. Find 3 to 5 specific, physically "
        "observed details or defects — never generic adjectives. A scratch across "
        "the lid. A half-peeled price sticker. A chipped corner. A coffee ring on "
        "the base. Three wilted leaves. A bent prong. Sun-faded plastic on one side "
        "only, and not the other. Prefer the oddly specific over the safely general: "
        "'a scratch near the hinge, roughly a centimetre long' beats 'some wear'. "
        "These quirks get reused verbatim in marketing copy later, so describe what "
        "is actually in THIS photo, not what a stock photo of this object usually "
        "looks like.\n\n"
        "Return ONLY a JSON object with exactly these keys, no markdown, no code "
        "fences, no commentary:\n"
        '  "object": the object, two words or fewer\n'
        '  "quirks": an array of 3 to 5 short strings, each one specific observed detail\n'
        '  "material": the primary material\n'
        '  "condition": one or two words, e.g. "pristine", "well-loved", "barely surviving"'
    )


def build_content_prompt(vision: VisionResult, tone: Tone) -> str:
    return "TODO"


def build_logo_prompt(pack: ContentPack) -> str:
    return "TODO"
