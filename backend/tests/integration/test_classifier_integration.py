import pytest

from app.ml.classifier import classify
from app.ml.labels import LABELS


@pytest.mark.slow
def test_real_classification_inference():
    text = "El lavarropas hace un ruido muy fuerte y no gira el tambor, parece que el motor se quemó."
    result = classify(text)

    assert result.label in LABELS
    assert result.confidence > 0.0
    assert result.status in ["CLASSIFIED", "LOW_CONFIDENCE"]
    print(
        f"Real inference result: {result.label} ({result.confidence}) - {result.status}"
    )
