"""
Runtime classification service used by the API layer.

Loads the trained TF-IDF vectorizer + two Logistic Regression models
(category, priority). If artifacts are missing (e.g. first run), it trains
them on the spot from complaints/ml/training_data.py.

A small set of safety-critical keywords acts as a guardrail layer on top of
the statistical model: if a complaint mentions something like fire, gas leak,
or physical threats, priority is never downgraded below High even if the
model itself is less confident. This mirrors how real moderation/triage
systems usually combine an ML model with deterministic safety rules.
"""

import os
import threading

import joblib

from .train_model import (
    ARTIFACT_DIR,
    CATEGORY_MODEL_PATH,
    PRIORITY_MODEL_PATH,
    VECTORIZER_PATH,
    train,
)

_lock = threading.Lock()
_cache = {}

SAFETY_OVERRIDE_KEYWORDS = [
    'fire', 'smoke', 'gas leak', 'explosion', 'electrocut',
    'weapon', 'knife', 'gun', 'assault', 'attacked', 'threatened',
    'molest', 'harass', 'rape', 'stalk', 'suicide', 'self harm',
    'collapsed', 'short circuit', 'sparking', 'unconscious',
]


def _load_or_train():
    with _lock:
        if _cache:
            return _cache['vectorizer'], _cache['category_model'], _cache['priority_model']

        if not (os.path.exists(VECTORIZER_PATH)
                and os.path.exists(CATEGORY_MODEL_PATH)
                and os.path.exists(PRIORITY_MODEL_PATH)):
            os.makedirs(ARTIFACT_DIR, exist_ok=True)
            vectorizer, category_model, priority_model = train(verbose=False)
        else:
            vectorizer = joblib.load(VECTORIZER_PATH)
            category_model = joblib.load(CATEGORY_MODEL_PATH)
            priority_model = joblib.load(PRIORITY_MODEL_PATH)

        _cache['vectorizer'] = vectorizer
        _cache['category_model'] = category_model
        _cache['priority_model'] = priority_model
        return vectorizer, category_model, priority_model


def classify(text: str):
    """
    Returns a dict: {category, priority, confidence, safety_override}
    confidence is the model's own probability for the predicted category,
    rounded to 2 decimals - used purely for transparency in the dashboard.
    """
    vectorizer, category_model, priority_model = _load_or_train()

    X = vectorizer.transform([text])

    category = str(category_model.predict(X)[0])
    priority = str(priority_model.predict(X)[0])

    cat_proba = category_model.predict_proba(X)[0]
    confidence = float(max(cat_proba))

    safety_override = False
    lowered = text.lower()
    if any(keyword in lowered for keyword in SAFETY_OVERRIDE_KEYWORDS):
        safety_override = True
        priority = 'High'
        if category not in ('Safety', 'Ragging & Harassment'):
            # Don't blindly overwrite category, but nudge toward Safety if the
            # model picked something clearly unrelated and a hard trigger fired.
            category = 'Safety'

    return {
        'category': category,
        'priority': priority,
        'confidence': round(confidence, 2),
        'safety_override': safety_override,
    }
