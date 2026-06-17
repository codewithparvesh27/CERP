# ACE ABI Configuration-Driven Correction Engine

Full-stack starter application using:

- React + TypeScript frontend
- Python FastAPI backend
- PostgreSQL database
- Configuration-driven correction rules
- Fixed-length ACE ABI request/response parsing

## What it does

1. Accepts original ACE ABI request message.
2. Accepts ACE ABI response/rejection message.
3. Uses error configuration to map ACE response condition codes to request fields and UI views.
4. Produces correction work items for the UI.
5. Accepts user corrections.
6. Patches the original 80-character ACE request records.
7. Generates revised ACE request message with CRLF line endings.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Frontend:

```text
http://localhost:5173
```

Backend API:

```text
http://localhost:8000/docs
```

## Demo flow

1. Open the UI.
2. Paste the sample request from `samples/ace_request_sample.txt`.
3. Paste the sample response from `samples/ace_response_sample.txt`.
4. Click **Create Correction Session**.
5. Review generated correction work items.
6. Enter corrected values.
7. Generate revised ACE request.

## Important

This starter contains representative field mappings for common ESF records and response records. Extend:

- `config/error_config.sample.json`
- `backend/app/domain/field_specs.py`
- `backend/app/services/correlation.py`

for additional ACE/CATAIR records and production-grade rules.
