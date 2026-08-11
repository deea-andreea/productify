# Productify — starter scaffold

A working **walking skeleton**: photo in, pitch page out, end to end, using
canned/hardcoded data instead of real OpenAI calls. Nobody is blocked —
every lane can build against this while the real API calls get wired in.

## Run it (30 seconds)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000** — upload any photo, pick a tone, click
generate. You'll get a pitch page for a stapler (the canned vision result)
in whatever tone you picked, and it'll show up in the gallery below.

Copy `backend/.env.example` to `backend/.env` and drop in the mentor-provided
key once you're ready to wire in real calls. `pipeline.py` doesn't load it
yet — that's the first thing the pipeline-backend lane should add
(`from dotenv import load_dotenv; load_dotenv()` + `from openai import OpenAI`).

## Project layout

```
productify/
  backend/
    main.py              FastAPI app: routes + orchestration
    schemas.py            <-- THE CONTRACT. Pydantic models everyone codes against.
    pipeline.py            The 4 pipeline steps (look/invent/brand/publish)
    templates/
      pitch_template.html  Jinja2 template, inline CSS, embeds images as base64
    storage/               uploads/, pitches/, gallery.json (all just files, no DB)
  frontend/
    index.html            Upload + tone selector + gallery UI
    app.js                 Calls the backend, renders the gallery
```

## Who touches what (maps to the brief's 4 lanes)

### Lane 1 — Pipeline backend → `pipeline.py`, `main.py`
Replace the canned bodies of `look_at_photo()` and `invent_content()`:
- `look_at_photo`: one gpt-5-mini vision call. Base64-encode the photo,
  send with a prompt asking for the `VisionResult` shape, using Structured
  Outputs (`schemas.VisionResult.model_json_schema()`).
- `invent_content`: one Structured Outputs call for the full `ContentPack`
  (including the `Theme`), prompted with the vision result + tone. Keep this
  ONE call, not five — that's the brief's explicit guidance.
- Resize the photo client-side before it hits this endpoint (see frontend
  lane) so you're not base64-ing a 12MP photo.

### Lane 2 — Template & theming → `templates/pitch_template.html`, `generate_logo()`
- Wire `generate_logo()` to gpt-image-1. Save the returned PNG instead of
  the placeholder SVG. Keep the "publish immediately with placeholder,
  swap logo in later" pattern from the brief if you have time — it hides
  the image-gen latency.
- Push on the template's visual design — this is a big chunk of "does the
  audience enjoy it."
- Keep everything self-contained: no external font/CSS/JS requests, only
  embedded base64 images. That's already true in the current template —
  don't break it when you extend it.

### Lane 3 — Frontend → `frontend/`
- Add real camera capture (the `capture="environment"` attribute on the
  file input already nudges mobile browsers to open the camera).
- Resize/compress images client-side before upload (canvas + toBlob at
  ~1200px is plenty).
- Build out the gallery page/viewer, download-as-.html button (backend
  already exposes `GET /pitch/{slug}/download`).
- Add the YOLO-mode toggle here when you get to it (just another form field).

### Lane 4 — Prompt lab & demo
- Doesn't need to touch code much at first. Use the running skeleton to:
  - draft/iterate the 4 tone prompts against real object photos
  - tune the gpt-image-1 logo prompt
  - pick 2-3 demo objects that reliably produce great copy
  - write the 5-minute demo script

## The JSON contract (read this before you write pipeline code)

`schemas.py` is the single source of truth for what flows between steps.
If you need to add a field, say so in the team chat first — `main.py` and
the template both depend on these shapes staying in sync.

## Must-haves checklist (from the brief)

- [x] End-to-end pipeline scaffold (currently canned, wire in real calls)
- [x] Tone selector (4 tones already produce visibly different copy)
- [x] Gallery (list + open, each downloadable as a single .html file)

## Stretch goals — where they'd hook in

- **YOLO mode**: add a `yolo: bool` form field; if true, skip
  `invent_content` + template rendering and instead have one model call
  write the entire HTML page directly. Compare side-by-side with the
  templated version.
- **Elevator pitch (TTS)**: after `invent_content`, one TTS call over the
  hero copy; embed the returned audio as a base64 `<audio>` tag in the
  template.
- **VC verdict**: after `publish_page`, one more model call reviewing the
  content pack, returning a score + one-liner; render it as a badge.
- **QR code**: generate one for `/pitch/{slug}` (e.g. the `qrcode` pip
  package) and embed it in the template as a base64 PNG.
