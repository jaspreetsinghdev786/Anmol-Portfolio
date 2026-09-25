# Anmolpreet Singh - Video Editor Portfolio

A one-page portfolio for **Anmolpreet Singh**, video editor. The page is styled like an edit suite: a running timecode in the header, a pinned "timeline" where scrolling scrubs a playhead across his featured edits, a filterable bin with every clip, and a services list laid out as an edit decision list.

Plain HTML, CSS and JavaScript with no build step. GSAP (ScrollTrigger, SplitText) and Lenis load from jsDelivr.

## Run it locally

```bash
python serve.py          # http://localhost:3000
python serve.py 3100     # or pick another port
```

Use `serve.py` rather than opening the file directly. The page uses ES modules, and the server answers HTTP Range requests, which the videos need for streaming and seeking.

## Adding or changing videos

1. Put the source files in one folder, then add each file to the `CLIPS` map in `tools/transcode.py` with a slug.
2. Run `python tools/transcode.py "C:/path/to/Portfolio"` (needs FFmpeg on PATH). For each clip it writes:
   - `media/posters/<slug>.webp`: still frame
   - `media/previews/<slug>.mp4`: 6 s muted loop for cards and the timeline
   - `media/full/<slug>.mp4`: 720p H.264/AAC for the player
   Clips that already have output are skipped.
3. Add the clip to `CLIPS` in `js/clips.js` with its title, category and duration. Set `featured: true` to also put it on the timeline strip.

## Brand palette

| Hex | Name | Used for |
|---|---|---|
| `#EADEDA` | Dust Grey | Text |
| `#353535` | Graphite | Surfaces |
| `#ED474A` | Strawberry Red | REC dot, playhead, CTAs |
| `#AF5D63` | Dusty Mauve | Secondary accent |
| `#7F9172` | Dusty Olive | Category labels, waveform |

Type: Big Shoulders Display (headlines), Instrument Sans (body), JetBrains Mono (timecode and labels).

## Files

```text
index.html          page markup
css/styles.css      design tokens and all styles
js/clips.js         clip list, categories, timecode helpers
js/main.js          builds the grid, timeline and player, and runs the motion
media/              generated web video (see above)
tools/transcode.py  source video -> web media
serve.py            local server with Range support
```
