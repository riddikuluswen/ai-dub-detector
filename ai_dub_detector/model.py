import numpy as np

from .paths import DEFAULT_CACHE_DIR

DEFAULT_MODEL_ID = "Hemgg/Deepfake-audio-detection"


class ModelLoadError(RuntimeError):
    pass


class AudioDeepfakeModel:
    def __init__(self, model_id: str = DEFAULT_MODEL_ID, device: str = "auto") -> None:
        self.model_id = model_id
        try:
            import torch
            from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

            self.torch = torch
            self.device = _pick_device(torch, device)
            DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            self.extractor = AutoFeatureExtractor.from_pretrained(
                model_id,
                cache_dir=str(DEFAULT_CACHE_DIR),
            )
            self.model = AutoModelForAudioClassification.from_pretrained(
                model_id,
                cache_dir=str(DEFAULT_CACHE_DIR),
            )
        except Exception as exc:  # pragma: no cover - depends on network/model cache
            raise ModelLoadError(f"模型加载失败: {model_id}. 原因: {exc}") from exc

        self.model.to(self.device)
        self.model.eval()
        self.id2label = {str(k): str(v) for k, v in self.model.config.id2label.items()}

    def score(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> tuple[float, str, float, dict[str, float]]:
        inputs = self.extractor(
            audio,
            sampling_rate=sample_rate,
            return_tensors="pt",
            padding=True,
        )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with self.torch.no_grad():
            logits = self.model(**inputs).logits[0]
            probs = self.torch.softmax(logits, dim=-1).detach().cpu().numpy()

        raw_scores = {}
        for idx, score in enumerate(probs):
            label = self.model.config.id2label.get(idx, f"LABEL_{idx}")
            raw_scores[str(label)] = float(score)

        top_idx = int(np.argmax(probs))
        top_label = str(self.model.config.id2label.get(top_idx, f"LABEL_{top_idx}"))
        top_score = float(probs[top_idx])
        fake_probability = _infer_fake_probability(raw_scores)
        return fake_probability, top_label, top_score, raw_scores


def _pick_device(torch_module, device: str) -> str:
    if device != "auto":
        return device
    if torch_module.backends.mps.is_available():
        return "mps"
    if torch_module.cuda.is_available():
        return "cuda"
    return "cpu"


def _infer_fake_probability(raw_scores: dict[str, float]) -> float:
    fake_words = ("fake", "spoof", "synthetic", "generated", "ai", "clone", "cloned", "tts")
    real_words = ("real", "human", "genuine", "bonafide", "bona-fide", "authentic")

    fake_sum = sum(score for label, score in raw_scores.items() if _has_word(label, fake_words))
    if fake_sum > 0:
        return float(min(1.0, fake_sum))

    real_sum = sum(score for label, score in raw_scores.items() if _has_word(label, real_words))
    if real_sum > 0:
        return float(max(0.0, 1.0 - real_sum))

    if len(raw_scores) == 2:
        items = list(raw_scores.items())
        return float(items[1][1])

    return float(max(raw_scores.values()) if raw_scores else 0.0)


def _has_word(label: str, words) -> bool:
    lowered = label.lower()
    return any(word in lowered for word in words)
