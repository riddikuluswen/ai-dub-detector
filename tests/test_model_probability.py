import pytest

from ai_dub_detector.model import _infer_fake_probability


def test_fake_label_probability():
    assert _infer_fake_probability({"real": 0.2, "fake": 0.8}) == 0.8


def test_real_label_probability():
    assert _infer_fake_probability({"human": 0.7, "other": 0.3}) == pytest.approx(0.3)


def test_binary_unknown_labels_use_second_class():
    assert _infer_fake_probability({"LABEL_0": 0.4, "LABEL_1": 0.6}) == 0.6
