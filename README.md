# Ebhaan Diabetes Risk Calculator

This repository contains a FastAPI-based diabetes risk assessment app, including input forms, risk scoring logic, result visualization, and report assets.

## Run locally

```bash
cd "/Users/dcpanda/Desktop/Ebhaan Project"
python -m uvicorn DiabetesRiskCalc:app --host 127.0.0.1 --port 8001
```

Then open:

- `http://127.0.0.1:8001/`

## Files

- `DiabetesRiskCalc.py` — FastAPI application and risk calculator code
- `requirements.txt` — Python dependencies
- `report_assets/` — report images and manifest
- `templates/` — HTML templates

## GitHub Push

After creating a GitHub repository, run:

```bash
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```
