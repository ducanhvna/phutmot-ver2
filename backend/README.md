# FastAPI Multiprocessor Project

This project is a minimal FastAPI app ready for multiprocessor (multi-core) serving using Uvicorn.

## Development

```sh
uvicorn main:app --reload
```

## Production (multi-core)

```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Healthcheck

- Endpoint: `/healthcheck`
- Response: `{ "status": "ok" }`
