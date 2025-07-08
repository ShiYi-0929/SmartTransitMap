from fastapi import FastAPI
from detect.routes import router as detect_router

app = FastAPI()

app.include_router(detect_router, prefix="/api")
