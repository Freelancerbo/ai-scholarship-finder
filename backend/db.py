from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "ai_scholarship_finder.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text())


def seed_if_empty() -> None:
    from database.seed import SCHOLARSHIPS  # local import to avoid cycles

    with get_connection() as conn:
        existing = conn.execute("SELECT COUNT(*) FROM scholarships").fetchone()[0]
        if existing:
            return
        conn.executemany(
            """
            INSERT INTO scholarships (
                name, provider, description, country, education_level, field,
                min_gpa, max_income, min_age, max_age, award_amount, deadline
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    s["name"],
                    s["provider"],
                    s["description"],
                    s["country"],
                    s["education_level"],
                    s["field"],
                    s["min_gpa"],
                    s["max_income"],
                    s["min_age"],
                    s["max_age"],
                    s["award_amount"],
                    s["deadline"],
                )
                for s in SCHOLARSHIPS
            ],
        )
        conn.commit()


def save_student(profile: dict) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO students (name, age, country, education_level, gpa, field_of_study, income, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile["name"],
                profile["age"],
                profile["country"],
                profile["education_level"],
                profile["gpa"],
                profile["field_of_study"],
                profile["income"],
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
        return cursor.lastrowid


def fetch_scholarships() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM scholarships").fetchall()
