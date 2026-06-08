import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class MediaError(RuntimeError):
    pass


def require_ffmpeg() -> None:
    if not shutil.which("ffmpeg"):
        raise MediaError("找不到 ffmpeg。请先安装 ffmpeg，例如 macOS: brew install ffmpeg")


def probe_duration(path: Path) -> Optional[float]:
    if not shutil.which("ffprobe"):
        return None

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
        payload = json.loads(proc.stdout)
        duration = payload.get("format", {}).get("duration")
        return float(duration) if duration else None
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError):
        return None


def extract_audio(input_path: Path, output_wav: Path, max_duration: Optional[float] = None) -> Path:
    require_ffmpeg()
    output_wav.parent.mkdir(parents=True, exist_ok=True)

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(input_path)]
    if max_duration:
        cmd.extend(["-t", str(max_duration)])
    cmd.extend(["-vn", "-ac", "1", "-ar", "16000", "-f", "wav", str(output_wav)])

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise MediaError(f"ffmpeg 抽音频失败: {detail}") from exc

    return output_wav
