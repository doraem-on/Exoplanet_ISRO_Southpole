from fastapi import FastAPI

app = FastAPI(
    title="LMIP Backend API",
    description="Backend API for the Lunar Mission Intelligence Platform",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "LMIP Backend is running"}
