import tempfile
from pathlib import Path
from typing import Optional

from .media import extract_audio, probe_duration
from .model import DEFAULT_MODEL_ID, AudioDeepfakeModel
from .paths import DEFAULT_TMP_DIR
from .segmentation import detect_active_segments, load_audio, slice_segment
from .types import AnalysisResult, SegmentScore


def analyze_file(
    input_path: Path,
    model_id: str = DEFAULT_MODEL_ID,
    max_duration: Optional[float] = 90.0,
    max_segments: int = 12,
    keep_wav: Optional[Path] = None,
    device: str = "auto",
    calibration: str = "conservative",
) -> AnalysisResult:
    input_path = input_path.expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"文件不存在: {input_path}")

    media_duration = probe_duration(input_path)

    DEFAULT_TMP_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ai-dub-detector-", dir=DEFAULT_TMP_DIR) as tmpdir:
        wav_path = keep_wav or Path(tmpdir) / "audio.wav"
        extract_audio(input_path, wav_path, max_duration=max_duration)

        audio, sample_rate = load_audio(wav_path)
        segments = detect_active_segments(audio, sample_rate, top_k=max_segments)
        model = AudioDeepfakeModel(model_id=model_id, device=device)

        scored_segments = []
        for segment in segments:
            chunk = slice_segment(audio, sample_rate, segment)
            if chunk.size == 0:
                continue
            probability, top_label, top_score, raw_scores = model.score(chunk, sample_rate)
            scored_segments.append(
                SegmentScore(
                    start=segment.start,
                    end=segment.end,
                    duration=segment.duration,
                    ai_probability=probability,
                    top_label=top_label,
                    top_score=top_score,
                    raw_scores=raw_scores,
                )
            )

    active_audio_duration = sum(seg.duration for seg in segments)
    analyzed_duration = sum(seg.duration for seg in scored_segments)
    overall_score = _weighted_score(scored_segments)
    max_score = max((seg.ai_probability for seg in scored_segments), default=0.0)
    warnings = _build_warnings(
        media_duration=media_duration,
        active_audio_duration=active_audio_duration,
        scored_count=len(scored_segments),
        max_duration=max_duration,
    )

    return AnalysisResult(
        input_path=str(input_path),
        model_id=model_id,
        calibration=calibration,
        risk=_risk_label(
            overall_score,
            max_score,
            active_audio_duration,
            scored_segments,
            calibration,
        ),
        overall_score=overall_score,
        max_segment_score=max_score,
        media_duration=media_duration,
        active_audio_duration=active_audio_duration,
        analyzed_duration=analyzed_duration,
        segment_count=len(scored_segments),
        segments=scored_segments,
        warnings=warnings,
        model_labels=getattr(model, "id2label", {}),
    )


def _weighted_score(segments) -> float:
    total = sum(seg.duration for seg in segments)
    if total <= 0:
        return 0.0
    return float(sum(seg.ai_probability * seg.duration for seg in segments) / total)


def _risk_label(
    overall_score: float,
    max_score: float,
    active_audio_duration: float,
    segments,
    calibration: str,
) -> str:
    if active_audio_duration < 5:
        return "样本不足"

    segment_count = len(segments)
    if segment_count == 0:
        return "样本不足"

    if calibration == "sensitive":
        if overall_score >= 0.75 or max_score >= 0.88:
            return "高"
        if overall_score >= 0.55 or max_score >= 0.72:
            return "中"
        return "低"

    if calibration == "balanced":
        medium_count = sum(seg.ai_probability >= 0.82 for seg in segments)
        if overall_score >= 0.82 or (max_score >= 0.92 and medium_count >= 2):
            return "高"
        if overall_score >= 0.65 or max_score >= 0.82:
            return "中"
        return "低"

    high_count = sum(seg.ai_probability >= 0.90 for seg in segments)
    medium_count = sum(seg.ai_probability >= 0.80 for seg in segments)
    high_ratio = high_count / segment_count

    if (
        active_audio_duration >= 15
        and high_count >= 2
        and high_ratio >= 0.35
        and overall_score >= 0.90
    ):
        return "高"
    if max_score >= 0.97 and overall_score >= 0.84 and high_count >= 2:
        return "高"
    if medium_count >= 2 and overall_score >= 0.80:
        return "中"
    if max_score >= 0.93 and overall_score >= 0.70:
        return "中"
    return "低"


def _build_warnings(media_duration, active_audio_duration, scored_count, max_duration):
    warnings = []
    if scored_count == 0:
        warnings.append("没有检测到可分析的人声片段。")
    if active_audio_duration < 15:
        warnings.append("有效人声偏短，结果只能作为弱信号。")
    if max_duration and media_duration and media_duration > max_duration:
        warnings.append(f"只分析了前 {max_duration:.0f} 秒，长视频建议截取重点片段再测。")
    warnings.append("模型输出是筛查分数，不适合作为单独证据。")
    return warnings
