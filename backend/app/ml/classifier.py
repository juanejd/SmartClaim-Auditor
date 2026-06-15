from pydantic import BaseModel
from transformers import pipeline
from app.ml.labels import MODEL_LABELS, LABEL_MAPPING
from app.core.config import CLASSIFIER_THRESHOLD


class ClassificationResult(BaseModel):
    label: str
    confidence: float
    status: str


MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

classifier_pipeline = pipeline("zero-shot-classification", model=MODEL_NAME)

classifier_pipeline(
    "Este es un texto de prueba para el calentamiento.", candidate_labels=MODEL_LABELS
)


def classify(text: str) -> ClassificationResult:
    # el modelo recibe etiquetas en espa;ol
    result = classifier_pipeline(text, candidate_labels=MODEL_LABELS)

    print("Result: ", result)
    """
    {'sequence': 'Usé lavandina pura para limpiar por dentro el lavarropas y se arruinaron todas las gomas y sellos internos, ahora pierde agua.', 'labels': ['daño físico', 'error de operación', 'otro', 'garantía financiera', 'falla eléctrica'], 'scores': [0.864890992641449, 0.11464628577232361, 0.011254933662712574, 0.006961103528738022, 0.0022467360831797123]}
    """

    top_model_label = result["labels"][0]
    top_score = result["scores"][0]

    # mantener consistencia en db y se retorna en el modelo
    top_label = LABEL_MAPPING[top_model_label]

    if top_score < CLASSIFIER_THRESHOLD:
        status = "LOW_CONFIDENCE"
    else:
        status = "CLASSIFIED"

    return ClassificationResult(label=top_label, confidence=top_score, status=status)
