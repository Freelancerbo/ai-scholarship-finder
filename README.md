# AI Scholarship Finder System

AI Scholarship Finder System is a full-stack web application that collects student profiles and recommends scholarships using a lightweight AI/ML similarity model. The system stores student submissions and scholarship data in SQLite and provides personalized match scores with eligibility explanations.

## Features

- Flask backend with REST endpoint and server-rendered homepage.
- Student profile form (name, age, country, education level, GPA, field of study, income).
- AI-driven recommendation engine with cosine similarity scoring.
- Eligibility rules for GPA, income, age, country, field, and education level.
- SQLite database storing student profiles and 20+ scholarships.
- Clean folder structure: `backend`, `frontend`, `database`, `model`.

## Project Structure

```
.
├── backend
│   ├── app.py
│   ├── db.py
│   ├── recommender.py
│   └── requirements.txt
├── database
│   ├── ai_scholarship_finder.db (auto-generated)
│   ├── schema.sql
│   └── seed.py
├── frontend
│   ├── static
│   │   ├── app.js
│   │   └── style.css
│   └── templates
│       └── index.html
├── model
│   └── model.json (auto-generated)
└── README.md
```

## Local Setup

### 1) Create a virtual environment (optional but recommended)

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 3) Initialize the database with sample scholarships

```bash
python database/seed.py
```

### 4) Run the Flask server

```bash
python backend/app.py
```

The application will be available at `http://localhost:5000`.

## How the AI/ML Recommendation Works

1. Scholarship data is vectorized with one-hot encoding for country, field, and education level.
2. Numeric requirements (GPA, income, age) are normalized using dataset statistics.
3. The model computes cosine similarity between the student profile vector and each scholarship vector.
4. Eligibility rules apply hard filters and annotate reasons for ineligibility.
5. The UI displays the top matches with match scores and eligibility notes.

## Adding More Scholarships

Edit `database/seed.py` to add new scholarship entries, then re-run:

```bash
python database/seed.py
```

This will populate the SQLite database if it is empty.

## Notes

- `database/ai_scholarship_finder.db` and `model/model.json` are generated automatically.
- The recommendation engine runs locally without external services.
