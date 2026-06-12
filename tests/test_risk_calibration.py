from ai_dub_detector.analyzer import _risk_label
from ai_dub_detector.types import SegmentScore


def segment(score: float) -> SegmentScore:
    return SegmentScore(
        start=0,
        end=10,
        duration=10,
        ai_probability=score,
        top_label="AIVoice",
        top_score=score,
        raw_scores={"AIVoice": score, "HumanVoice": 1 - score},
    )


def test_conservative_does_not_escalate_single_spike():
    segments = [segment(0.95), segment(0.40), segment(0.35)]

    risk = _risk_label(0.57, 0.95, 30, segments, "conservative")

    assert risk == "低"


def test_conservative_requires_repeated_high_scores():
    segments = [segment(0.94), segment(0.92), segment(0.91), segment(0.88)]

    risk = _risk_label(0.91, 0.94, 40, segments, "conservative")

    assert risk == "高"


def test_sensitive_keeps_old_behavior():
    segments = [segment(0.73)]

    risk = _risk_label(0.50, 0.73, 10, segments, "sensitive")

    assert risk == "中"
