# 🧠 PhishGuard — ML Service

Flask-based REST API serving a Random Forest phishing detection model.
Part of the [PhishGuard](https://github.com/jagdeep2001kainth/phish-guard-frontend) project.

## Endpoints
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Predict phishing probability |

## Tech Stack
- Python, Flask, scikit-learn, Random Forest, TF-IDF

## Running Locally
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Part of PhishGuard
- Frontend: [phish-guard-frontend](https://github.com/jagdeep2001kainth/phish-guard-frontend)
- Backend: [phish-guard-backend](https://github.com/jagdeep2001kainth/phish-guard-backend)
