CREATE TABLE IF NOT EXISTS scholarships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    description TEXT NOT NULL,
    country TEXT NOT NULL,
    education_level TEXT NOT NULL,
    field TEXT NOT NULL,
    min_gpa REAL NOT NULL,
    max_income INTEGER NOT NULL,
    min_age INTEGER NOT NULL,
    max_age INTEGER NOT NULL,
    award_amount INTEGER NOT NULL,
    deadline TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    country TEXT NOT NULL,
    education_level TEXT NOT NULL,
    gpa REAL NOT NULL,
    field_of_study TEXT NOT NULL,
    income INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
