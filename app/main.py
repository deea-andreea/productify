"""
The FastAPI app: routes + orchestration. See contracts/api.md for the
request/response shapes this file must honor.
"""

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app import config, pipeline, storage
from app.models import ContentPack, Tone, VisionResult
# Importing these submodules by name is what makes them reachable as
# pipeline.vision / pipeline.content / pipeline.image / pipeline.prompts
# below -- a plain `from app import pipeline` would otherwise leave that
# namespace empty (app/pipeline/__init__.py doesn't import them itself).
from app.pipeline import content, image, prompts, vision  # noqa: F401
from app.render import render_pitch

logger = logging.getLogger(__name__)


def _seed_gallery_from_fixtures() -> None:
    """Populate the gallery from fixtures/bundles/ on a fresh checkout, so
    the demo never opens to an empty gallery. Never allowed to prevent
    startup — fixtures/bundles may not exist yet, or a bundle may be
    malformed, and neither should take the server down.
    """
    try:
        if storage.list_pitches():
            return
        bundles_dir = Path("fixtures/bundles")
        if not bundles_dir.is_dir():
            return
        bundle_dirs = sorted(
            p for p in bundles_dir.iterdir() if p.is_dir() and (p / "bundle.json").exists()
        )
        if not bundle_dirs:
            return
        for bundle_dir in bundle_dirs:
            bundle = json.loads((bundle_dir / "bundle.json").read_text(encoding="utf-8"))
            pack = ContentPack.model_validate(bundle["pack"])
            photo_bytes = (bundle_dir / "photo.jpg").read_bytes()
            logo_path = bundle_dir / "logo.png"
            logo_bytes = logo_path.read_bytes() if logo_path.exists() else None
            html = render_pitch(pack, photo_bytes, logo_bytes)
            slug = storage.slugify(pack.brand.name)
            meta = {
                "slug": slug,
                "brand_name": pack.brand.name,
                "tagline": pack.tagline,
                "tone": bundle.get("tone", ""),
                "url": f"/pitch/{slug}",
                "download_url": f"/pitch/{slug}/download",
                "thumb_url": f"/pitch/{slug}/photo.jpg",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "logo_status": "ready" if logo_bytes is not None else "failed",
            }
            storage.save_pitch(slug, pack, html, photo_bytes, meta)
    except Exception:
        logger.warning("Seeding gallery from fixtures/bundles failed; starting with an empty gallery.", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _seed_gallery_from_fixtures()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _finish_logo(slug: str, pack: ContentPack, photo_bytes: bytes) -> None:
    """Background task kicked off after the pitch response is already sent.
    gpt-image-1 is slow (and mocked as always-None today), so the client
    never waits on it — see contracts/handoff.md's async logo pattern.
    """
    logo_bytes = await pipeline.image.generate_logo(pack)
    if logo_bytes is not None:
        new_html = render_pitch(pack, photo_bytes, logo_bytes)
        storage.overwrite_html(slug, new_html)
        storage.update_meta(slug, logo_status="ready")
    else:
        storage.update_meta(slug, logo_status="failed")


@app.post("/api/pitch")
async def create_pitch(
    background_tasks: BackgroundTasks,
    photo: UploadFile = File(...),
    tone: str = Form(...),
):
    try:
        tone_enum = Tone(tone)
    except ValueError:
        raise HTTPException(400, detail=f"Invalid tone: {tone!r}")

    photo_bytes = await photo.read()
    if not photo_bytes:
        raise HTTPException(400, detail="Empty photo upload.")

    # Vision failures never surface as an error (contracts/api.md) — fall
    # back to a generic VisionResult so the demo never hard-fails on a bad
    # photo or a flaky vision call.
    try:
        vision_result = await pipeline.vision.analyze_image(photo_bytes)
    except Exception:
        logger.warning("Vision analysis failed; falling back to a generic VisionResult.", exc_info=True)
        vision_result = VisionResult(
            object="an object",
            quirks=[],
            material="unknown material",
            condition="condition unknown",
        )

    try:
        pack = await pipeline.content.generate_content(vision_result, tone_enum)
    except Exception:
        logger.warning("Content generation failed.", exc_info=True)
        raise HTTPException(502, detail="The model had a bad moment. Try again.")

    slug = storage.slugify(pack.brand.name)
    html = render_pitch(pack, photo_bytes, None)
    meta = {
        "slug": slug,
        "brand_name": pack.brand.name,
        "tagline": pack.tagline,
        "tone": tone_enum.value,
        "url": f"/pitch/{slug}",
        "download_url": f"/pitch/{slug}/download",
        "thumb_url": f"/pitch/{slug}/photo.jpg",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "logo_status": "pending",
    }
    storage.save_pitch(slug, pack, html, photo_bytes, meta)

    background_tasks.add_task(_finish_logo, slug, pack, photo_bytes)

    return {
        "slug": slug,
        "url": f"/pitch/{slug}",
        "brand_name": pack.brand.name,
        "tone": tone_enum.value,
        "logo_status": "pending",
    }


@app.get("/api/pitch/{slug}")
async def get_pitch_meta(slug: str):
    try:
        return storage.load_meta(slug)
    except FileNotFoundError:
        raise HTTPException(404, detail=f"No pitch found for slug {slug!r}.")


@app.get("/api/gallery")
async def get_gallery():
    return storage.list_pitches()


@app.get("/pitch/{slug}")
async def get_pitch_page(slug: str):
    try:
        return HTMLResponse(storage.load_html(slug))
    except FileNotFoundError:
        raise HTTPException(404, detail=f"No pitch found for slug {slug!r}.")


@app.get("/pitch/{slug}/download")
async def download_pitch(slug: str):
    html_path = Path(config.settings.OUT_DIR) / slug / "index.html"
    if not html_path.exists():
        raise HTTPException(404, detail=f"No pitch found for slug {slug!r}.")
    return FileResponse(html_path, filename=f"{slug}.html", media_type="text/html")


@app.get("/pitch/{slug}/photo.jpg")
async def get_pitch_photo(slug: str):
    photo_path = storage.photo_path(slug)
    if not photo_path.exists():
        raise HTTPException(404, detail=f"No photo found for slug {slug!r}.")
    return FileResponse(photo_path, media_type="image/jpeg")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/stats")
async def get_stats():
    return {
        "pitches_total": len(storage.list_pitches()),
        "image_calls_used": config.image_calls_used(),
        "image_calls_remaining": config.image_calls_remaining(),
        "avg_elapsed_ms": 0,
    }


# Must stay last: mounted at "/" so it only catches what the explicit API
# routes above don't.
app.mount("/", StaticFiles(directory="web", html=True), name="web")
