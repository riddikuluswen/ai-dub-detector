from ai_dub_detector.report import to_text
from ai_dub_detector.types import AnalysisResult, SegmentScore


def test_text_report_contains_core_fields():
    result = AnalysisResult(
        input_path="/tmp/a.mp4",
        model_id="test/model",
        risk="高",
        overall_score=0.82,
        max_segment_score=0.91,
        media_duration=42.0,
        active_audio_duration=18.0,
        analyzed_duration=18.0,
        segment_count=1,
        segments=[
            SegmentScore(
                start=4.2,
                end=11.8,
                duration=7.6,
                ai_probability=0.91,
                top_label="fake",
                top_score=0.91,
                raw_scores={"real": 0.09, "fake": 0.91},
            )
        ],
        warnings=["模型输出是筛查分数。"],
    )

    text = to_text(result)

    assert "AI 配音嫌疑：高" in text
    assert "00:04-00:12" in text
    assert "test/model" in text
