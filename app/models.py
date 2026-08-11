"""
Pydantic v2 models mirroring contracts/content_pack.schema.json.

This is THE shared contract between Station 1 (Perception & Generation) and
Station 2 (Presentation). Do not add or rename a field without updating the
JSON schema and telling the other station — everything downstream assumes
these shapes.
"""

from enum import Enum

from pydantic import BaseModel, Field


class Tone(str, Enum):
    vc = "vc"
    luxury = "luxury"
    infomercial = "infomercial"
    kickstarter = "kickstarter"


TONE_LABELS: dict[Tone, str] = {
    Tone.vc: "Silicon Valley Startup",
    Tone.luxury: "Luxury Brand",
    Tone.infomercial: "Late-Night Infomercial",
    Tone.kickstarter: "Kickstarter Campaign",
}


class VisionResult(BaseModel):
    object: str
    quirks: list[str] = Field(default_factory=list)
    material: str
    condition: str


class Brand(BaseModel):
    name: str
    slug_hint: str
    personality: str


class Hero(BaseModel):
    headline: str
    subhead: str
    cta_label: str


class Feature(BaseModel):
    title: str
    body: str
    icon_hint: str = "sparkle"


class PricingTier(BaseModel):
    tier: str
    price: str
    period: str
    bullets: list[str] = Field(default_factory=list)
    highlighted: bool = False


class Testimonial(BaseModel):
    quote: str
    author: str
    role: str


class CTA(BaseModel):
    headline: str
    button_label: str
    footnote: str


HEX_COLOR = r"^#[0-9a-fA-F]{6}$"


class Palette(BaseModel):
    """Hex-validated so these values are safe to interpolate directly into
    inline SVG attributes and CSS custom properties outside Jinja's
    autoescaping (see app/render/package.py's monogram_svg)."""

    bg: str = Field(pattern=HEX_COLOR)
    surface: str = Field(pattern=HEX_COLOR)
    text: str = Field(pattern=HEX_COLOR)
    muted: str = Field(pattern=HEX_COLOR)
    accent: str = Field(pattern=HEX_COLOR)
    accent_contrast: str = Field(pattern=HEX_COLOR)


class Theme(BaseModel):
    palette: Palette
    font_pair: str = "geometric"
    radius: str = "soft"
    mood: str = "corporate"


class ContentPack(BaseModel):
    vision: VisionResult
    brand: Brand
    tagline: str
    hero: Hero
    features: list[Feature]
    pricing: list[PricingTier]
    testimonials: list[Testimonial]
    cta: CTA
    theme: Theme
    logo_prompt: str
