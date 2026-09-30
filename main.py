from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .database import Base, engine
from .routers import books, members, borrowing


# -------------------------------------------------------------
# Create database tables
# -------------------------------------------------------------

Base.metadata.create_all(bind=engine)


# -------------------------------------------------------------
# FastAPI application
# -------------------------------------------------------------

app = FastAPI(
    title="Library Management API",
    description=(
        "REST API for managing books, members, "
        "borrowing and returning books."
    ),
    version="1.0.0",
)


# -------------------------------------------------------------
# Validation error handler
# -------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )


# -------------------------------------------------------------
# Root endpoint
# -------------------------------------------------------------

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Library Management API is running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


# -------------------------------------------------------------
# Health check
# -------------------------------------------------------------

@app.get("/health", tags=["Root"])
def health_check():
    return {
        "status": "healthy"
    }


# -------------------------------------------------------------
# Register routers
# -------------------------------------------------------------

app.include_router(books.router)
app.include_router(members.router)
app.include_router(borrowing.router)