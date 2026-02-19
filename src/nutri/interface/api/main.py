from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from nutri.interface.api import routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Nutri API",
    description="REST API for Nutri-Score calculation.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.nutri_router)


@app.get("/")
def welcome():
    return "Welcome to the ATNi API."


@app.get("/test")
def test():
    return {"score": 10, "grade": "A"}
