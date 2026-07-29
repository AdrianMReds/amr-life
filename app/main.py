from fastapi import FastAPI, HTTPException

from app.api.auth import router as auth_router
from app.api.tasks import router as task_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router, tags=['auth'])
app.include_router(task_router, tags=['tasks'])

