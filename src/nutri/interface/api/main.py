from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from nutri.interface.api import routers
from nutri.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


_is_prod = get_settings().env == "prod"

app = FastAPI(
    title="Nutri API",
    description="REST API for Nutri-Score calculation.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
    openapi_url=None if _is_prod else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,  # ty: ignore[invalid-argument-type]
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.nutri_router)
app.include_router(routers.hsr_router)
app.include_router(routers.survey_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [{"field": e["loc"][-1], "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={
            "message": "Invalid product data. Please check the submitted values.",
            "errors": errors,
        },
    )


@app.get("/")
def welcome():
    return "Welcome to the ATNi API."


@app.get("/test")
def test():
    return {"score": 10, "grade": "A"}
