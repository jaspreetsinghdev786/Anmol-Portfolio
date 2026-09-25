"""Transcode the raw edits into web-ready media.

For every source clip this writes, under media/:
  posters/<slug>.webp   still frame used before the video loads
  previews/<slug>.mp4   6 s muted loop, 360 px wide, for the grid
  full/<slug>.mp4       720 px wide H.264 + AAC, faststart, for the player

Run:  python tools/transcode.py "C:/path/to/Portfolio"
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "media"

# source file -> (slug, where in the clip the preview loop starts, as a fraction)
CLIPS = {
    "1 (1).mp4": ("creator-intro", 0.30),
    "1.mp4": ("garage-hook-a", 0.10),
    "C1.mp4": ("garage-hook-b", 0.10),
    "2.mp4": ("tonino-01", 0.20),
    "3.mp4": ("tonino-02", 0.20),
    "4.mp4": ("tonino-03", 0.25),
    "5.mp4": ("tonino-04", 0.20),
    "6.mp4": ("tonino-05", 0.20),
    "a1.mp4": ("tonino-06", 0.25),
    "SD 2.mp4": ("ran-from-the-scene", 0.15),
    "Bodylines jeep.mp4": ("bodylines-jeep", 0.30),
    "SD REEL 1.mp4": ("herds-of-comedy-01", 0.30),
    "SD REEL 2.mp4": ("herds-of-comedy-02", 0.30),
    "reel 1.mp4": ("improv-01", 0.35),
    "reel 2.mp4": ("improv-02", 0.35),
    "reel 3.mp4": ("improv-03", 0.35),
    "Dinosaur Final.mp4": ("dinosaur", 0.30),
    "Final Dodo.mp4": ("dodo", 0.30),
    "Titanic.mp4": ("titanic", 0.30),
    "final bdelloid.mp4": ("bdelloid", 0.30),
    "coco sample xray.mp4": ("xray", 0.30),
    "Final v2.mp4": ("border-explainer", 0.20),
    "Sample Documentry.mp4": ("documentary-sample", 0.30),
    "optimization.mp4": ("honey-optimization", 0.20),
    "WED 1.mp4": ("wedding-night", 0.30),
}


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height:format=duration", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    data = json.loads(out)
    s = data["streams"][0]
    return float(data["format"]["duration"]), s["width"], s["height"]


def main(src_dir):
    src_dir = Path(src_dir)
    for sub in ("posters", "previews", "full"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    meta = {}
    for name, (slug, at) in CLIPS.items():
        src = src_dir / name
        dur, w, h = probe(src)
        start = max(0.0, min(dur * at, dur - 6.5))
        landscape = w > h
        # scale by the short side so vertical and horizontal clips get the same sharpness
        full_scale = "scale=1280:-2" if landscape else "scale=720:-2"
        prev_scale = "scale=640:-2" if landscape else "scale=360:-2"

        poster = OUT / "posters" / f"{slug}.webp"
        preview = OUT / "previews" / f"{slug}.mp4"
        full = OUT / "full" / f"{slug}.mp4"

        if not poster.exists():
            run(["-ss", f"{start + 1:.2f}", "-i", str(src), "-frames:v", "1",
                 "-vf", full_scale, "-q:v", "78", str(poster)])
        if not preview.exists():
            run(["-ss", f"{start:.2f}", "-t", "6", "-i", str(src), "-an",
                 "-vf", f"{prev_scale},fps=25", "-c:v", "libx264", "-preset", "slow",
                 "-crf", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(preview)])
        if not full.exists():
            run(["-i", str(src), "-vf", full_scale, "-c:v", "libx264", "-preset", "medium",
                 "-crf", "26", "-maxrate", "3M", "-bufsize", "6M", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(full)])

        meta[slug] = {"duration": round(dur, 2), "orientation": "landscape" if landscape else "portrait"}
        print(f"done {slug}", flush=True)

    (OUT / "meta.json").write_text(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Jaspreet Singh\Downloads\Portfolio\Portfolio")
