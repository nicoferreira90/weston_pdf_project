from fastapi import FastAPI

app = FastAPI(title="Weston contract extraction", version="0.1.0")


@app.get("/api/health", tags=["setup"])
def health() -> dict[str, str]:
    return {"status": "ok"}
