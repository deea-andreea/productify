"""
Flat-file storage. No database — each pitch is a folder under OUT_DIR.

  out/pitches/{slug}/
    index.html   the rendered, self-contained page (overwritten when the logo lands)
    pitch.json   the ContentPack, for debugging / re-export as a bundle
    photo.jpg    the uploaded product photo
    meta.json    gallery-facing summary, per contracts/api.md
"""

import json
import random
import string
from pathlib import Path

from app.config import settings
from app.models import ContentPack


def _out_dir() -> Path:
    return Path(settings.OUT_DIR)


def slugify(brand_name: str) -> str:
    base = "".join(c.lower() if c.isalnum() else "-" for c in brand_name).strip("-")
    while "--" in base:
        base = base.replace("--", "-")
    base = base or "startup"
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{base}-{suffix}"


def save_pitch(slug: str, pack: ContentPack, html: str, photo_bytes: bytes, meta: dict) -> Path:
    pitch_dir = _out_dir() / slug
    pitch_dir.mkdir(parents=True, exist_ok=True)
    (pitch_dir / "index.html").write_text(html, encoding="utf-8")
    (pitch_dir / "pitch.json").write_text(pack.model_dump_json(indent=2), encoding="utf-8")
    (pitch_dir / "photo.jpg").write_bytes(photo_bytes)
    (pitch_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return pitch_dir


def update_meta(slug: str, **fields) -> dict:
    meta = load_meta(slug)
    meta.update(fields)
    (_out_dir() / slug / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def overwrite_html(slug: str, html: str) -> None:
    (_out_dir() / slug / "index.html").write_text(html, encoding="utf-8")


def load_meta(slug: str) -> dict:
    meta_path = _out_dir() / slug / "meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(slug)
    return json.loads(meta_path.read_text(encoding="utf-8"))


def load_html(slug: str) -> str:
    html_path = _out_dir() / slug / "index.html"
    if not html_path.exists():
        raise FileNotFoundError(slug)
    return html_path.read_text(encoding="utf-8")


def photo_path(slug: str) -> Path:
    return _out_dir() / slug / "photo.jpg"


def list_pitches() -> list[dict]:
    out_dir = _out_dir()
    if not out_dir.exists():
        return []
    entries = []
    for meta_path in out_dir.glob("*/meta.json"):
        try:
            entries.append(json.loads(meta_path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    entries.sort(key=lambda e: e.get("created_at", ""), reverse=True)
    return entries
