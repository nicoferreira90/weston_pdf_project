from fastapi import FastAPI

from app.api.extraction import router as extraction_router

app = FastAPI(title="Weston contract extraction", version="0.1.0")
app.include_router(extraction_router)


@app.get("/api/health", tags=["setup"])
def health() -> dict[str, str]:
    return {"status": "ok"}
