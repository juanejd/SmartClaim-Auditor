LABEL_MAPPING = {
    "falla eléctrica": "ELECTRICAL_FAILURE",
    "error de operación": "OPERATION_ERROR",
    "garantía financiera": "FINANCIAL_WARRANTY",
    "daño físico": "PHYSICAL_DAMAGE",
    "otro": "OTHER",
}

MODEL_LABELS = list(LABEL_MAPPING.keys())
LABELS = list(LABEL_MAPPING.values())
