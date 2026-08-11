# OWNED BY STATION 2. Signature is frozen. Do not implement or edit here.
from app.models import ContentPack


def render_pitch(pack: ContentPack, photo_bytes: bytes, logo_bytes: bytes | None) -> str:
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        f"<title>{pack.brand.name}</title></head><body>"
        f"<h1>{pack.brand.name}</h1><p>{pack.tagline}</p>"
        "<p>Placeholder render — Station 2 replaces this.</p>"
        "</body></html>"
    )
