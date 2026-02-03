from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.db import init_db, save_student, seed_if_empty  # noqa: E402
from backend.recommender import recommend_scholarships  # noqa: E402

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
)


@app.before_first_request
def setup_database() -> None:
    init_db()
    seed_if_empty()


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/recommend")
def recommend():
    payload = request.get_json(silent=True) or request.form.to_dict()
    try:
        profile = {
            "name": payload["name"].strip(),
            "age": int(payload["age"]),
            "country": payload["country"].strip(),
            "education_level": payload["education_level"],
            "gpa": float(payload["gpa"]),
            "field_of_study": payload["field_of_study"].strip(),
            "income": int(payload["income"]),
        }
    except (KeyError, ValueError) as exc:
        return jsonify({"error": "Invalid input", "details": str(exc)}), 400

    save_student(profile)
    recommendations = recommend_scholarships(profile)

    return jsonify({"student": profile, "recommendations": recommendations})


if __name__ == "__main__":
    init_db()
    seed_if_empty()
    app.run(host="0.0.0.0", port=5000, debug=True)
