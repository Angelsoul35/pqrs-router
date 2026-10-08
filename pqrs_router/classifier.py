"""Classify a citizen request into a PQRS type and a target department.

Two linear models share one TF-IDF vectoriser: one predicts the request type
(petition / complaint / claim / suggestion / report), the other the department.
Both are logistic regressions, so a prediction can be explained by the words that
drove it — useful when a routing decision is questioned.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .generate import make_dataset
from .taxonomy import Department, RequestType


@dataclass
class Classification:
    request_type: RequestType
    type_confidence: float
    department: Department
    department_confidence: float
    top_terms: list[tuple[str, float]] = field(default_factory=list)


class RequestClassifier:
    def __init__(self) -> None:
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
        self._type = LogisticRegression(max_iter=1000, C=4.0)
        self._dept = LogisticRegression(max_iter=1000, C=4.0)
        self._fitted = False

    def fit(
        self,
        texts: list[str] | None = None,
        y_type: list[str] | None = None,
        y_dept: list[str] | None = None,
    ) -> RequestClassifier:
        if texts is None:
            texts, y_type, y_dept = make_dataset()
        x = self._vectorizer.fit_transform(texts)
        self._type.fit(x, y_type)
        self._dept.fit(x, y_dept)
        self._fitted = True
        return self

    def _explain(self, x_row, model, class_index: int, k: int = 4) -> list[tuple[str, float]]:
        coef = model.coef_[class_index]
        contributions = x_row.toarray().ravel() * coef
        terms = self._vectorizer.get_feature_names_out()
        order = np.argsort(contributions)[::-1]
        return [
            (terms[i], round(float(contributions[i]), 4))
            for i in order
            if contributions[i] > 0
        ][:k]

    def classify(self, text: str) -> Classification:
        if not self._fitted:
            raise RuntimeError("Classifier is not fitted. Call fit() first.")
        x = self._vectorizer.transform([text])

        type_proba = self._type.predict_proba(x)[0]
        t_idx = int(np.argmax(type_proba))
        request_type = RequestType(self._type.classes_[t_idx])

        dept_proba = self._dept.predict_proba(x)[0]
        d_idx = int(np.argmax(dept_proba))
        department = Department(self._dept.classes_[d_idx])

        return Classification(
            request_type=request_type,
            type_confidence=round(float(type_proba[t_idx]), 4),
            department=department,
            department_confidence=round(float(dept_proba[d_idx]), 4),
            top_terms=self._explain(x, self._type, t_idx),
        )
