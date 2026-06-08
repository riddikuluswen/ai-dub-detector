from pathlib import Path

import numpy as np
import soundfile as sf

from .types import AudioSegment


def load_audio(path: Path, sample_rate: int = 16000):
    audio, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    if sr != sample_rate:
        raise ValueError(f"音频采样率应为 {sample_rate}Hz，当前是 {sr}Hz。请先用 ffmpeg 转换。")
    return audio.astype(np.float32), sr


def detect_active_segments(
    audio: np.ndarray,
    sample_rate: int,
    min_segment_sec: float = 2.5,
    max_segment_sec: float = 15.0,
    padding_sec: float = 0.25,
    top_k: int = 12,
) -> list[AudioSegment]:
    if audio.size == 0:
        return []

    frame_length = int(sample_rate * 0.03)
    hop_length = int(sample_rate * 0.01)
    rms = _rms_frames(audio, frame_length, hop_length)

    if float(np.max(rms)) < 1e-5:
        return []

    threshold = max(float(np.quantile(rms, 0.70)) * 0.70, float(np.max(rms)) * 0.08, 1e-4)
    active = rms >= threshold

    ranges = _boolean_ranges(active)
    segments = []
    for start_frame, end_frame in ranges:
        start = max(0.0, start_frame * hop_length / sample_rate - padding_sec)
        end = min(len(audio) / sample_rate, end_frame * hop_length / sample_rate + padding_sec)
        if end - start >= min_segment_sec:
            segments.extend(_split_segment(start, end, max_segment_sec))

    if not segments:
        duration = len(audio) / sample_rate
        fallback_end = min(duration, max_segment_sec)
        if fallback_end >= 1.0:
            segments.append(AudioSegment(0.0, fallback_end, fallback_end))

    segments.sort(key=lambda seg: seg.duration, reverse=True)
    selected = segments[:top_k]
    selected.sort(key=lambda seg: seg.start)
    return selected


def slice_segment(audio: np.ndarray, sample_rate: int, segment: AudioSegment) -> np.ndarray:
    start = max(0, int(segment.start * sample_rate))
    end = min(len(audio), int(segment.end * sample_rate))
    return audio[start:end]


def _boolean_ranges(values: np.ndarray):
    ranges = []
    start = None
    for idx, value in enumerate(values):
        if value and start is None:
            start = idx
        elif not value and start is not None:
            ranges.append((start, idx))
            start = None
    if start is not None:
        ranges.append((start, len(values)))
    return ranges


def _rms_frames(audio: np.ndarray, frame_length: int, hop_length: int) -> np.ndarray:
    if len(audio) < frame_length:
        return np.array([float(np.sqrt(np.mean(np.square(audio))))], dtype=np.float32)

    frame_count = 1 + (len(audio) - frame_length) // hop_length
    values = np.empty(frame_count, dtype=np.float32)
    for idx in range(frame_count):
        start = idx * hop_length
        frame = audio[start : start + frame_length]
        values[idx] = float(np.sqrt(np.mean(np.square(frame))))
    return values


def _split_segment(start: float, end: float, max_segment_sec: float) -> list[AudioSegment]:
    duration = end - start
    if duration <= max_segment_sec:
        return [AudioSegment(start=start, end=end, duration=duration)]

    segments = []
    current = start
    while current < end:
        chunk_end = min(current + max_segment_sec, end)
        if chunk_end - current >= 1.0:
            segments.append(
                AudioSegment(start=current, end=chunk_end, duration=chunk_end - current)
            )
        current = chunk_end
    return segments
