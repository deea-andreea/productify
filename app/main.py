import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from app import config, storage
from app.config import ROOT, settings
from app.models import Tone

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("productify")

app = FastAPI(title="Productify", version="0.1.0")

# Wide open. Hackathon, one day, local network, no auth.
# allow_credentials must stay False: browsers reject "*" combined with credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Station 2's whole frontend, served from the same origin so no proxy is needed.
# Mounted here at the scaffold so Station 2 never has to edit this file.
app.mount("/web", StaticFiles(directory=ROOT / "web", html=True), name="web")


# --- STUB DATA -------------------------------------------------------------
# Every route below returns hardcoded data shaped exactly like contracts/api.md.
# T1-T4 replace the bodies; the shapes do not change.

STUB_SLUG = "clipwell-a3f9k"

STUB_FIELDS = {
    "status": "ready",
    "logo_status": "pending",
    "tone": "vc",
    "brand": "ClipWell",
    "tagline": "The last stapler you will ever onboard.",
    "object": "stapler",
    "created_at": "2026-08-11T09:41:02Z",
    "elapsed_ms": 18420,
}


def summary(slug: str, **overrides) -> dict:
    """A PitchSummary per contracts/api.md. The three URLs are always derived from
    the slug so they can never disagree with it — Station 2 polls this shape."""
    return {
        **STUB_FIELDS,
        "slug": slug,
        "pitch_url": f"/pitch/{slug}",
        "download_url": f"/pitch/{slug}/download",
        "thumb_url": f"/pitch/{slug}/photo.jpg",
        **overrides,
    }

STUB_PAGE = (
    "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
    "<title>Productify — stub pitch</title></head><body>"
    "<h1>Stub pitch page</h1>"
    "<p>The real page arrives once the pipeline is wired up.</p>"
    "</body></html>"
)


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "mock": settings.MOCK}


@app.get("/api/stats")
async def stats() -> dict:
    used = config.image_calls_used()
    return {
        "pitches_total": len(storage.list_pitches()),
        "image_calls_used": used,
        "image_calls_remaining": max(0, settings.MAX_IMAGE_CALLS - used),
        "avg_elapsed_ms": 0,
    }


@app.post("/api/pitch")
async def create_pitch(image: UploadFile = File(...), tone: str = Form(...)) -> dict:
    if tone not in {t.value for t in Tone}:
        raise HTTPException(status_code=400, detail=f"Unknown tone: {tone!r}")
    if image.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(status_code=400, detail="Upload a JPEG or a PNG.")

    # STUB — T4 wires vision -> content -> render -> save, plus the logo background task.
    log.info("stub POST /api/pitch tone=%s filename=%s", tone, image.filename)
    return summary(STUB_SLUG, tone=tone)


@app.get("/api/pitch/{slug}")
async def get_pitch(slug: str) -> dict:
    # STUB — T4 returns the live meta.json so the frontend can poll logo_status.
    return summary(slug)


@app.get("/api/gallery")
async def gallery() -> dict:
    # STUB — the real list comes from storage.list_pitches().
    items = [summary(STUB_SLUG)]
    return {"count": len(items), "items": items}


@app.get("/pitch/{slug}", response_class=HTMLResponse)
async def pitch_page(slug: str) -> HTMLResponse:
    # STUB — T4 serves out/pitches/{slug}/index.html.
    return HTMLResponse(STUB_PAGE)


@app.get("/pitch/{slug}/download", response_class=HTMLResponse)
async def pitch_download(slug: str) -> HTMLResponse:
    return HTMLResponse(
        STUB_PAGE,
        headers={"Content-Disposition": f'attachment; filename="{slug}.html"'},
    )


@app.get("/pitch/{slug}/photo.jpg")
async def pitch_photo(slug: str) -> Response:
    photo = storage.pitch_dir(slug) / "photo.jpg"
    if not photo.exists():
        raise HTTPException(status_code=404, detail="No photo for that slug.")
    return Response(photo.read_bytes(), media_type="image/jpeg")
