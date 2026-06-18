"""
Trains the complaint classification engine:

    raw text --> TF-IDF vectorizer --> Logistic Regression (category)
                                    --> Logistic Regression (priority)

Run with:  python manage.py shell -c "from complaints.ml.train_model import train; train()"
or simply: python complaints/ml/train_model.py   (run from backend/ with Django not required)

Saves three artifacts (vectorizer + 2 classifiers) to complaints/ml/artifacts/
using joblib, so the trained model survives server restarts.
"""

import os

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from .training_data import TRAINING_DATA

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), 'artifacts')
VECTORIZER_PATH = os.path.join(ARTIFACT_DIR, 'vectorizer.joblib')
CATEGORY_MODEL_PATH = os.path.join(ARTIFACT_DIR, 'category_model.joblib')
PRIORITY_MODEL_PATH = os.path.join(ARTIFACT_DIR, 'priority_model.joblib')


def train(verbose=True):
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    texts = [row[0] for row in TRAINING_DATA]
    categories = [row[1] for row in TRAINING_DATA]
    priorities = [row[2] for row in TRAINING_DATA]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1,
        max_features=4000,
    )
    X = vectorizer.fit_transform(texts)

    X_train, X_test, y_cat_train, y_cat_test, y_pri_train, y_pri_test = train_test_split(
        X, categories, priorities, test_size=0.2, random_state=42, stratify=categories,
    )

    category_model = LogisticRegression(max_iter=2000, C=4.0)
    category_model.fit(X_train, y_cat_train)

    priority_model = LogisticRegression(max_iter=2000, C=4.0, class_weight='balanced')
    priority_model.fit(X_train, y_pri_train)

    if verbose:
        cat_acc = accuracy_score(y_cat_test, category_model.predict(X_test))
        pri_acc = accuracy_score(y_pri_test, priority_model.predict(X_test))
        print(f'Category model held-out accuracy: {cat_acc:.2f}')
        print(f'Priority model held-out accuracy: {pri_acc:.2f}')

    # Refit on the FULL dataset before saving, so the deployed model uses all
    # available labeled examples (the split above was only for evaluation).
    category_model_full = LogisticRegression(max_iter=2000, C=4.0)
    category_model_full.fit(X, categories)

    priority_model_full = LogisticRegression(max_iter=2000, C=4.0, class_weight='balanced')
    priority_model_full.fit(X, priorities)

    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(category_model_full, CATEGORY_MODEL_PATH)
    joblib.dump(priority_model_full, PRIORITY_MODEL_PATH)

    if verbose:
        print(f'Saved artifacts to {ARTIFACT_DIR}')

    return vectorizer, category_model_full, priority_model_full


if __name__ == '__main__':
    train()
