# Harvest Credit

Harvest Credit is a Python MVP for South African smallholder farmers who access seed, fertilizer, and drought insurance through a farming cooperative. Farmers receive inputs on credit and repay after harvest. When simulated weather data falls below the insured rainfall threshold, the system automatically pays down the credit line instead of sending cash to the farmer.

## Features

- FastAPI backend with phone number + cooperative PIN login
- Cooperative staff flow for farmer registration and KYC confirmation
- Explainable approval rules: verified cooperative, verified KYC, supported crop, farm size of at least 0.5 hectares, and a ZAR 50,000 starting cap
- Input package catalog with optional drought insurance add-on
- SQLAlchemy models and Alembic migration, using SQLite by default and portable numeric/date types for Postgres
- Daily APScheduler job for idempotent rainfall-index payout checks
- Harvest-time repayment recording for cash, mobile money, or cooperative collection
- Cooperative dashboard counts and SMS/USSD-style farmer summary
- Streamlit demo UI with large controls and English, Afrikaans, and isiZulu labels

## Run locally

```bash
cd projects/harvest-credit
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for the API explorer. In a second terminal, with the virtual environment active:

```bash
cd projects/harvest-credit
streamlit run streamlit_app.py
```

The seed script creates 3 cooperatives, 10 farmers, 3 input packages, 4 active credit lines, and historical weather readings for 6 September 2026. Limpopo receives 8 mm against a 20 mm drought threshold, so one payout is automatically created and applied to the first credit line. The seed is idempotent; delete `harvest_credit.db` to rebuild the demo.

## Useful API calls

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/dashboard
curl -X POST http://localhost:8000/api/weather/check-triggers
curl http://localhost:8000/api/farmers/1/sms-summary
```

The main flows are available under `/api`: farmer registration and KYC, `/input-packages`, `/credit-lines`, repayments, weather readings, trigger checks, login, dashboard, and SMS summaries.

## Demo boundaries

This is an MVP, not a production financial service. Weather readings are loaded from `data/weather.csv`; the OpenWeatherMap/pyowm adapter is not connected. Authentication is intentionally a simple demo PIN flow and has no session tokens, rate limiting, or encrypted identity storage. ID photo capture stores only a filename. Mobile money is represented by a repayment method and has no payment-provider integration. The scheduled job runs in the API process and should move to a separate worker for production. Real KYC, consent, audit logs, encryption, South African regulatory review, and Postgres deployment remain before handling real farmer data or money.

## Project layout

```text
harvest-credit/
├── app/                 # FastAPI, SQLAlchemy models, schemas, and services
├── alembic/             # Initial database migration
├── data/weather.csv     # Simulated rainfall index input
├── seed.py              # Repeatable demo dataset
├── streamlit_app.py     # Cooperative-facing demo UI
├── requirements.txt
└── README.md
```
