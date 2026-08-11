# API contract

Frozen at scaffold time. If a field needs to change, say so out loud to the other
station before editing — both `app/main.py` and `web/*` depend on this staying stable.

Base URL: same origin. `app/main.py` mounts `web/` as `StaticFiles` at `/`, so the
frontend and the API are served by one process on one port.

## Tones

| value | label | voice |
|---|---|---|
| `vc` | Silicon Valley Startup | category creation, metrics-as-poetry, $/seat/month |
| `luxury` | Luxury Brand | restraint, invented heritage, "price on request" |
| `infomercial` | Late-Night Infomercial | second person, urgency, $19.99 in three easy payments |
| `kickstarter` | Kickstarter Campaign | community language, stretch goals, early-bird pricing |

## `POST /api/pitch`

Multipart form:
- `photo`: file (required)
- `tone`: one of the values above (required)

Returns immediately — does **not** wait for the logo (see `handoff.md` on the
async logo pattern):

```json
{
  "slug": "staple-io-a1b2c",
  "url": "/pitch/staple-io-a1b2c",
  "brand_name": "Staple.io",
  "tone": "vc",
  "logo_status": "pending"
}
```

Errors: `400` bad tone / empty photo. `502` `{"detail": "The model had a bad moment. Try again."}`
on a content-generation failure. Vision failures never surface as an error — they
fall back to a generic `VisionResult` so the demo never hard-fails.

## `GET /api/pitch/{slug}`

Poll this after `POST /api/pitch` to find out when the logo is ready.

```json
{
  "slug": "staple-io-a1b2c",
  "brand_name": "Staple.io",
  "tagline": "Fastening, reimagined.",
  "tone": "vc",
  "url": "/pitch/staple-io-a1b2c",
  "download_url": "/pitch/staple-io-a1b2c/download",
  "thumb_url": "/pitch/staple-io-a1b2c/photo.jpg",
  "created_at": "2026-08-11T10:00:00Z",
  "logo_status": "pending"
}
```

`logo_status` is one of `pending`, `ready`, `failed`. The page is valid HTML in all
three states — a missing/failed logo just means the inline monogram stays.

## `GET /api/gallery`

```json
[
  { "slug": "...", "brand_name": "...", "tagline": "...", "tone": "vc",
    "url": "...", "download_url": "...", "thumb_url": "...",
    "created_at": "...", "logo_status": "ready" }
]
```

Newest first.

## `GET /pitch/{slug}`

Returns the rendered, self-contained HTML page (`Content-Type: text/html`).

## `GET /pitch/{slug}/download`

Same HTML, as a file attachment named `{slug}.html`.

## `GET /pitch/{slug}/photo.jpg`

The uploaded product photo, for gallery thumbnails.

## `GET /health`

`{"status": "ok"}`

## `GET /api/stats`

```json
{ "pitches_total": 12, "image_calls_used": 9, "image_calls_remaining": 31,
  "avg_elapsed_ms": 4200 }
```
