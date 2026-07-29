from fastapi import FastAPI, HTTPException

from app.api.auth import router as auth_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router, tags=['auth'])

