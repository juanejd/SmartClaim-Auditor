from unittest.mock import patch
from app.ml.classifier import classify
from app.ml.labels import LABELS


@patch("app.ml.classifier.classifier_pipeline")
def test_classify_returns_known_label(mock_pipeline):
    mock_pipeline.return_value = {
        "labels": ["falla eléctrica", "otro"],
        "scores": [0.85, 0.15],
    }

    result = classify("El televisor hizo cortocircuito y se quemó")

    assert result.label == "ELECTRICAL_FAILURE"
    assert result.label in LABELS
    assert result.confidence == 0.85
    assert result.status == "CLASSIFIED"


@patch("app.ml.classifier.classifier_pipeline")
def test_low_confidence_sets_status(mock_pipeline):
    mock_pipeline.return_value = {
        "labels": ["otro", "error de operación"],
        "scores": [0.55, 0.45],
    }

    result = classify("Texto ambiguo sin mucho sentido")

    assert result.label == "OTHER"
    assert result.confidence == 0.55
    assert result.status == "LOW_CONFIDENCE"
