import pytest
from unittest.mock import MagicMock, patch
import app.ml.classifier as classifier_module
from app.ml.classifier import classify
from app.ml.labels import LABELS


@pytest.fixture(autouse=True)
def reset_pipeline_singleton():
    original = classifier_module._pipeline
    classifier_module._pipeline = None
    yield
    classifier_module._pipeline = original


def test_classify_returns_known_label():
    mock_pipeline = MagicMock(
        return_value={
            "labels": ["falla eléctrica", "otro"],
            "scores": [0.85, 0.15],
        }
    )

    with patch("app.ml.classifier._pipeline", mock_pipeline):
        result = classify("El televisor hizo cortocircuito y se quemó")

    assert result.label == "ELECTRICAL_FAILURE"
    assert result.label in LABELS
    assert result.confidence == 0.85
    assert result.status == "CLASSIFIED"


def test_low_confidence_sets_status():
    mock_pipeline = MagicMock(
        return_value={
            "labels": ["otro", "error de operación"],
            "scores": [0.55, 0.45],
        }
    )

    with patch("app.ml.classifier._pipeline", mock_pipeline):
        result = classify("Texto ambiguo sin mucho sentido")

    assert result.label == "OTHER"
    assert result.confidence == 0.55
    assert result.status == "LOW_CONFIDENCE"
