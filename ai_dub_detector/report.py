import json
from dataclasses import asdict
from pathlib import Path

from .types import AnalysisResult


def to_json(result: AnalysisResult, pretty: bool = True) -> str:
    payload = asdict(result)
    if pretty:
        return json.dumps(payload, ensure_ascii=False, indent=2)
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def save_json(result: AnalysisResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_json(result), encoding="utf-8")


def to_text(result: AnalysisResult) -> str:
    lines = [
        f"AI 配音嫌疑：{result.risk}",
        "",
        f"综合分：{result.overall_score:.2f}",
        f"最高片段分：{result.max_segment_score:.2f}",
        f"有效人声：{result.active_audio_duration:.1f} 秒",
        f"分析片段：{result.segment_count} 段",
        f"模型：{result.model_id}",
    ]

    if result.media_duration:
        lines.append(f"媒体时长：{result.media_duration:.1f} 秒")

    suspicious = sorted(result.segments, key=lambda item: item.ai_probability, reverse=True)[:5]
    if suspicious:
        lines.extend(["", "可疑片段："])
        for item in suspicious:
            lines.append(
                f"{_timecode(item.start)}-{_timecode(item.end)}  "
                f"{item.ai_probability:.2f}  {item.top_label}:{item.top_score:.2f}"
            )

    if result.warnings:
        lines.extend(["", "备注："])
        lines.extend(f"- {warning}" for warning in result.warnings)

    return "\n".join(lines)


def _timecode(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    if hour:
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    return f"{minute:02d}:{second:02d}"
