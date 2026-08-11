# The handoff between stations

Same data, two forms. Station 1 (Perception & Generation) produces a `ContentPack`;
Station 2 (Presentation) turns it into a page. Neither form should block the other
station's progress.

## Form 1 — in-process function call

```python
def render_pitch(pack: ContentPack, photo_bytes: bytes, logo_bytes: bytes | None) -> str
```

Owned by Station 2, in `app/render/__init__.py`. Frozen signature — if Station 1
needs a new field (e.g. a QR code, a VC verdict), it goes **inside** `pack`
(or a new optional param is negotiated out loud), never a silent change to this
signature.

`app/main.py` (Station 1) calls this once synchronously with `logo_bytes=None` so
the response never waits on `gpt-image-1`'s latency, then again from a background
task once the logo is ready, overwriting the saved `index.html`.

## Form 2 — on disk, a bundle

A bundle is a folder Station 1 can drop without running any of their code, and
Station 2 can render without running any of Station 1's code:

```
fixtures/bundles/{name}/
  bundle.json   {"pack": {...ContentPack...}, "tone": "vc", "object": "stapler",
                 "created_at": "...", "has_logo": false}
  photo.jpg
  logo.png      (optional — present only if has_logo is true)
```

`fixtures/bundles/` is committed to git (see the `.gitignore` negation), unlike
`out/pitches/{slug}/` which is real runtime output and is not.

Station 2's development loop, all day, needs nothing from Station 1 after the
first bundles land:

```bash
git fetch && git checkout origin/feat/pipeline -- fixtures/bundles
python -m app.render.preview fixtures/bundles/stapler-vc --open
```

## Validation rules enforced in Python (not in the JSON schema)

Structured Outputs strict mode drops `pattern`/`minItems`/`maxItems`/`minLength`.
Station 1's `content.py` is responsible for enforcing these after parsing, before
a `ContentPack` ever reaches `render_pitch`:

- exactly 3 `features`, 3 `pricing` tiers, 2 `testimonials` — truncate if more,
  pad by duplicating the last item if fewer
- every `palette` value matches `^#[0-9a-fA-F]{6}$`; if any fails, replace the
  **entire** palette with `DEFAULT_PALETTE` (partial palettes look broken, not
  stylish)
- exactly one `pricing` tier has `highlighted=true`; if zero or several, force
  the middle one

Station 2's renderer and preview tool validate through the `ContentPack` Pydantic
model on load and fail loudly on a malformed bundle — never guess at a missing
field.
