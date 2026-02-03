from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from backend.db import fetch_scholarships

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "model" / "model.json"

EDUCATION_LEVELS = ["High School", "Associate", "Bachelor", "Master", "PhD"]


@dataclass
class ModelMetadata:
    countries: list[str]
    fields: list[str]
    education_levels: list[str]
    numeric_means: dict[str, float]
    numeric_stds: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "countries": self.countries,
            "fields": self.fields,
            "education_levels": self.education_levels,
            "numeric_means": self.numeric_means,
            "numeric_stds": self.numeric_stds,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "ModelMetadata":
        return cls(
            countries=payload["countries"],
            fields=payload["fields"],
            education_levels=payload["education_levels"],
            numeric_means=payload["numeric_means"],
            numeric_stds=payload["numeric_stds"],
        )


def normalize(value: float, mean: float, std: float) -> float:
    if std == 0:
        return 0.0
    return (value - mean) / std


def train_model(scholarships: Iterable[dict]) -> ModelMetadata:
    countries = sorted({s["country"] for s in scholarships})
    fields = sorted({s["field"] for s in scholarships})
    education_levels = [level for level in EDUCATION_LEVELS if level in {s["education_level"] for s in scholarships}]

    numeric_columns = {
        "min_gpa": [s["min_gpa"] for s in scholarships],
        "max_income": [s["max_income"] for s in scholarships],
        "min_age": [s["min_age"] for s in scholarships],
        "max_age": [s["max_age"] for s in scholarships],
        "award_amount": [s["award_amount"] for s in scholarships],
    }

    numeric_means = {key: sum(values) / len(values) for key, values in numeric_columns.items()}
    numeric_stds = {
        key: math.sqrt(sum((v - numeric_means[key]) ** 2 for v in values) / len(values))
        for key, values in numeric_columns.items()
    }

    metadata = ModelMetadata(
        countries=countries,
        fields=fields,
        education_levels=education_levels,
        numeric_means=numeric_means,
        numeric_stds=numeric_stds,
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_text(json.dumps(metadata.to_dict(), indent=2))
    return metadata


def load_model_metadata(scholarships: Iterable[dict]) -> ModelMetadata:
    if MODEL_PATH.exists():
        return ModelMetadata.from_dict(json.loads(MODEL_PATH.read_text()))
    return train_model(scholarships)


def education_rank(level: str) -> int:
    try:
        return EDUCATION_LEVELS.index(level)
    except ValueError:
        return 0


def one_hot(value: str, options: list[str]) -> list[int]:
    return [1 if option.lower() == value.lower() else 0 for option in options]


def vectorize_student(profile: dict, metadata: ModelMetadata) -> list[float]:
    vector = []
    vector.extend(one_hot(profile["country"], metadata.countries))
    vector.extend(one_hot(profile["field_of_study"], metadata.fields))
    vector.extend(one_hot(profile["education_level"], metadata.education_levels))

    vector.append(normalize(profile["gpa"], metadata.numeric_means["min_gpa"], metadata.numeric_stds["min_gpa"]))
    vector.append(normalize(profile["income"], metadata.numeric_means["max_income"], metadata.numeric_stds["max_income"]))
    vector.append(normalize(profile["age"], metadata.numeric_means["min_age"], metadata.numeric_stds["min_age"]))
    return vector


def vectorize_scholarship(scholarship: dict, metadata: ModelMetadata) -> list[float]:
    vector = []
    vector.extend(one_hot(scholarship["country"], metadata.countries))
    vector.extend(one_hot(scholarship["field"], metadata.fields))
    vector.extend(one_hot(scholarship["education_level"], metadata.education_levels))

    vector.append(normalize(scholarship["min_gpa"], metadata.numeric_means["min_gpa"], metadata.numeric_stds["min_gpa"]))
    vector.append(normalize(scholarship["max_income"], metadata.numeric_means["max_income"], metadata.numeric_stds["max_income"]))
    vector.append(normalize(scholarship["min_age"], metadata.numeric_means["min_age"], metadata.numeric_stds["min_age"]))
    return vector


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def check_eligibility(profile: dict, scholarship: dict) -> tuple[bool, list[str]]:
    reasons = []
    eligible = True

    if profile["gpa"] < scholarship["min_gpa"]:
        eligible = False
        reasons.append("GPA below minimum requirement")

    if profile["income"] > scholarship["max_income"]:
        eligible = False
        reasons.append("Income exceeds maximum threshold")

    if not (scholarship["min_age"] <= profile["age"] <= scholarship["max_age"]):
        eligible = False
        reasons.append("Age outside allowed range")

    if education_rank(profile["education_level"]) < education_rank(scholarship["education_level"]):
        eligible = False
        reasons.append("Education level below requirement")

    if scholarship["country"].lower() != "any" and profile["country"].lower() != scholarship["country"].lower():
        eligible = False
        reasons.append("Country does not match eligibility")

    if scholarship["field"].lower() != "any" and profile["field_of_study"].lower() != scholarship["field"].lower():
        eligible = False
        reasons.append("Field of study does not match")

    return eligible, reasons


def recommend_scholarships(profile: dict) -> list[dict]:
    scholarships = [dict(row) for row in fetch_scholarships()]
    metadata = load_model_metadata(scholarships)
    student_vector = vectorize_student(profile, metadata)

    recommendations = []
    for scholarship in scholarships:
        scholarship_vector = vectorize_scholarship(scholarship, metadata)
        similarity = cosine_similarity(student_vector, scholarship_vector)
        eligible, reasons = check_eligibility(profile, scholarship)

        match_score = max(0.0, similarity) * 100
        if eligible:
            match_score = min(100.0, match_score + 15)

        recommendations.append(
            {
                **scholarship,
                "match_score": round(match_score, 2),
                "eligible": eligible,
                "reasons": reasons,
            }
        )

    recommendations.sort(key=lambda item: item["match_score"], reverse=True)
    return recommendations
