"""
Prompt strings for the three model-calling pipeline steps (vision, content,
logo). These are draft prompts — a reasonable starting point for Station 1's
navigator to refine once the real OpenAI calls go in, not a final artifact.
Nothing here is on today's critical path (everything runs mocked), but the
strings are written to be usable as-is if nobody revisits them.
"""

from app.models import ContentPack, Tone, VisionResult

TONE_BRIEFS: dict[Tone, str] = {
    Tone.vc: (
        "Silicon Valley Startup. Vocabulary: category creation, platforms not "
        "products, 'unlock', 'scale', 'moat', metrics-as-poetry (uptime %, NPS, "
        "ARR, retention). Sentence rhythm: short, punchy, staccato declaratives, "
        "with the occasional 'we're not X, we're Y' reframe. Exaggerates: total "
        "addressable market, network effects, founder conviction. Never says "
        "'small', 'niche', or 'good enough' — a limitation is reframed as a "
        "roadmap item. Pricing: $/seat/month tiers, a free tier to drive "
        "adoption, an 'Enterprise — Contact us' tier that signals ambition."
    ),
    Tone.luxury: (
        "Luxury Brand. Vocabulary: restraint, invented heritage (an atelier, a "
        "founding year, a 'maison'), materials named lovingly, the occasional "
        "French or Italian loanword. Sentence rhythm: short, declarative, one "
        "adjective per sentence, room to breathe between claims. Exaggerates: "
        "provenance, scarcity, the hand of the maker. Never says 'cheap', "
        "'deal', 'sale', or 'affordable', and never uses an exclamation point. "
        "Pricing: 'price on request' for the top tier, understated numbers "
        "elsewhere, no discounting language, no urgency."
    ),
    Tone.infomercial: (
        "Late-Night Infomercial. Vocabulary: second-person direct address, "
        "urgency, rhetorical questions ('Tired of X?'), measured ALL CAPS for "
        "emphasis, 'But wait, there's more!'. Sentence rhythm: short bursts, "
        "exclamation points, escalating stacked claims. Exaggerates: speed, "
        "ease, and quantity ('now with 2X the Y!'), plus testimonial "
        "enthusiasm. Never hedges — no 'might' or 'somewhat'. Pricing: $19.99-"
        "style price points, 'three easy payments of', free bonus gifts, "
        "'call in the next 10 minutes'."
    ),
    Tone.kickstarter: (
        "Kickstarter Campaign. Vocabulary: community language ('we', "
        "'backers', 'the team'), gratitude, transparency about process. "
        "Sentence rhythm: warm, conversational, first-person plural, the "
        "occasional confessional aside. Exaggerates: the emotional stakes of "
        "the project succeeding and the closeness of the community. Never "
        "pretends everything went perfectly — stays transparent about at "
        "least one manufacturing hiccup or delay, and skips corporate jargon "
        "and hard guarantees. Pricing: early-bird tiers, stretch goals, "
        "backer thresholds ('$X gets you Y'), 'funding ends in N days'."
    ),
}


def build_vision_prompt() -> str:
    return (
        "You are looking at a single product photo. Identify the object, but "
        "the identification is the least interesting part of your job — what "
        "matters is the specific, physical evidence that this exact object has "
        "a history: scratches, dents, stains, chips, faded spots, sticker "
        "residue, worn edges, mismatched parts, anything a generic stock photo "
        "of the same object would not have. Prefer 3-5 concrete, specifically "
        "observed quirks over generic adjectives like 'used' or 'worn' — say "
        "where the mark is and roughly what it looks like. Also note the "
        "dominant material(s) and an honest one-line condition summary. Do "
        "not invent damage that visibly isn't there, but do not undersell real "
        "wear either — a pristine object should get a shorter quirks list "
        "rather than fabricated flaws. Return only the object, quirks, "
        "material, and condition fields."
    )


def build_content_prompt(vision: VisionResult, tone: Tone) -> str:
    brief = TONE_BRIEFS[tone]
    quirks = "; ".join(vision.quirks) if vision.quirks else "no notable quirks observed"
    return (
        f"You are the copywriter and brand designer for a pitch page selling "
        f"a single real object as though it were a product launch.\n\n"
        f"The object, from a vision analysis, is:\n"
        f"- object: {vision.object}\n"
        f"- material: {vision.material}\n"
        f"- condition: {vision.condition}\n"
        f"- quirks: {quirks}\n\n"
        f"Write in this voice:\n{brief}\n\n"
        f"Hard requirement: every single quirk listed above must reappear "
        f"somewhere in the copy (hero, features, or testimonials), reformulated "
        f"as a feature or selling point in the target voice — never apologize "
        f"for a quirk, sell it. Invent a brand name, tagline, hero section, "
        f"exactly 3 features, exactly 3 pricing tiers with exactly one marked "
        f"highlighted, exactly 2 testimonials, a closing CTA, a visual theme "
        f"(hex palette, font pairing, corner radius, mood) that matches the "
        f"tone, and a logo_prompt for a follow-up image model. Fill every "
        f"field of the ContentPack schema — do not leave any optional-seeming "
        f"field empty."
    )


def build_logo_prompt(pack: ContentPack) -> str:
    return (
        f"Design a flat vector logo mark for the brand '{pack.brand.name}', "
        f"whose personality is: {pack.brand.personality}. The mark should be "
        f"a single simple icon — absolutely no text, no letters, no words, no "
        f"typography of any kind. Use {pack.theme.palette.accent} as the "
        f"primary color of the mark. Centered composition, generous padding, "
        f"flat solid shapes (no gradients, no photorealism, no drop shadows), "
        f"high contrast, and simple enough to stay legible and recognizable "
        f"when scaled down to 32x32 pixels."
    )
