"""Assemble Simulation Chamber PNG frames into a press-play MP4.

Status: **partial_with_gaps** — flipbook / Ken-Burns stills, not photoreal motion.
Uses repo toolchain ffmpeg when system ffmpeg is absent.
Click audio is optional and tagged `flipbook-not-motion` (not an original score).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any


def find_ffmpeg() -> str | None:
    found = shutil.which("ffmpeg")
    if found:
        return found
    candidates = [
        Path("/usr/bin/ffmpeg"),
        Path("/usr/local/bin/ffmpeg"),
        Path(__file__).resolve().parents[4]
        / "runtime"
        / "toolchain"
        / "ffmpeg"
        / "usr"
        / "bin"
        / "ffmpeg",
        Path("/media/jon/New Volume/Mandala Rendering Software/runtime/toolchain/ffmpeg/usr/bin/ffmpeg"),
    ]
    # worktree parents: neural-cinematic -> adapters -> mrs -> repo
    repo = Path(__file__).resolve().parents[3]
    candidates.append(repo / "runtime" / "toolchain" / "ffmpeg" / "usr" / "bin" / "ffmpeg")
    # sibling Mandala checkout
    candidates.append(
        Path("/media/jon/New Volume/Mandala Rendering Software/runtime/toolchain/ffmpeg/usr/bin/ffmpeg")
    )
    for path in candidates:
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    return None


def write_click_wav(dest: Path, *, seconds: float = 1.0, rate: int = 22050) -> Path:
    """Minimal click bed — not Mythar / Beatbox score."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    n = max(1, int(seconds * rate))
    with wave.open(str(dest), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        frames = bytearray()
        for i in range(n):
            # sparse clicks every ~0.25s
            if i % (rate // 4) < 80:
                amp = 8000
            else:
                amp = 0
            frames += int(amp).to_bytes(2, "little", signed=True)
        wf.writeframes(bytes(frames))
    return dest


def assemble_flipbook_mp4(
    frame_paths: list[Path],
    out_mp4: Path,
    *,
    fps: float = 8.0,
    with_click: bool = True,
) -> dict[str, Any]:
    """Concat PNG frames → MP4. Tag as flipbook-not-motion."""
    ffmpeg = find_ffmpeg()
    out_mp4 = Path(out_mp4)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    if not frame_paths:
        return {
            "ok": False,
            "status": "declared",
            "gaps": ["no_frames"],
            "why": "no frames to assemble",
        }
    if not ffmpeg:
        return {
            "ok": False,
            "status": "declared",
            "gaps": ["ffmpeg_missing"],
            "why": "ffmpeg not found (system or runtime/toolchain)",
        }

    list_file = out_mp4.with_suffix(".ffconcat.txt")
    lines = ["ffconcat version 1.0"]
    dur = 1.0 / max(0.1, fps)
    for p in frame_paths:
        lines.append(f"file '{Path(p).resolve()}'")
        lines.append(f"duration {dur:.6f}")
    # last frame repeat for concat demuxer
    lines.append(f"file '{Path(frame_paths[-1]).resolve()}'")
    list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
    ]
    gaps = [
        "flipbook_not_true_3d_motion",
        "ken_burns_or_tint_proxy_frames",
        "not_movie_lane_infinity_assemble",
    ]
    wav: Path | None = None
    if with_click:
        wav = out_mp4.with_suffix(".click.wav")
        write_click_wav(wav, seconds=max(1.0, len(frame_paths) / max(0.1, fps)))
        cmd.extend(["-i", str(wav)])
        gaps.append("click_bed_not_original_score")
        gaps.append("flipbook-not-motion")

    # Video encode after all inputs; avoid -vf before second -i (ffmpeg rejects it).
    cmd.extend(
        [
            "-vf",
            f"fps={fps},scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
        ]
    )
    if with_click and wav is not None:
        cmd.extend(["-c:a", "aac", "-b:a", "96k", "-shortest"])
    cmd.append(str(out_mp4))
    run = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if run.returncode != 0 or not out_mp4.is_file():
        return {
            "ok": False,
            "status": "partial_with_gaps",
            "gaps": gaps + ["ffmpeg_mux_failed"],
            "why": (run.stderr or run.stdout or "")[-800:],
            "ffmpeg": ffmpeg,
        }
    return {
        "ok": True,
        "status": "partial_with_gaps",
        "path": str(out_mp4.resolve()),
        "bytes": out_mp4.stat().st_size,
        "fps": fps,
        "frameCount": len(frame_paths),
        "tag": "flipbook-not-motion",
        "gaps": gaps,
        "ffmpeg": ffmpeg,
        "claim": "Simulation Chamber press-play flipbook — not photoreal cinema",
    }
