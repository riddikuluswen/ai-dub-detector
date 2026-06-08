from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AudioSegment:
    start: float
    end: float
    duration: float


@dataclass
class SegmentScore:
    start: float
    end: float
    duration: float
    ai_probability: float
    top_label: str
    top_score: float
    raw_scores: dict[str, float]


@dataclass
class AnalysisResult:
    input_path: str
    model_id: str
    risk: str
    overall_score: float
    max_segment_score: float
    media_duration: Optional[float]
    active_audio_duration: float
    analyzed_duration: float
    segment_count: int
    segments: list[SegmentScore]
    warnings: list[str] = field(default_factory=list)
    model_labels: dict[str, str] = field(default_factory=dict)
