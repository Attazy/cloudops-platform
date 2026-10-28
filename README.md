# CloudOps Platform

A staged DevOps portfolio project. Stage 1 delivers a small REST API and automated tests.
Later stages will add Docker Compose/PostgreSQL, GitHub Actions, AWS/Terraform, ECR,
K3s/Kubernetes, automated deployment, security scanning, and monitoring.

## Stage 1: run locally

Requirements: Python 3.11+ (Python 3.12 recommended).

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pytest -v
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## API endpoints

- `GET /` - app information
- `GET /health` - liveness-style health endpoint
- `GET /ready` - stage-1 readiness endpoint (no database dependency yet)
- `GET /api/v1/services` - list service records
- `POST /api/v1/services` - create a service record
- `GET /api/v1/services/{service_id}` - get a record
- `DELETE /api/v1/services/{service_id}` - delete a record

Stage 1 stores records in process memory. Data is reset when the application restarts
and is not shared between multiple workers. PostgreSQL persistence is intentionally
introduced in a later stage.
