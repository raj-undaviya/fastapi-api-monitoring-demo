import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s request_id=%(request_id)s %(message)s",
)

logger = logging.getLogger("monitoring-demo")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI monitoring demo started", extra={"request_id": "startup"})
    yield
    logger.info("FastAPI monitoring demo stopped", extra={"request_id": "shutdown"})


app = FastAPI(
    title="FastAPI API Monitoring Demo",
    version="1.0.0",
    description="Sample API used to demonstrate health, performance, failures and alerting.",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "Unhandled application exception method=%s path=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
            extra={"request_id": request_id},
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        extra={"request_id": request_id},
    )

    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = request.headers.get("X-Request-ID", "generated-in-middleware")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id,
            "path": request.url.path,
        },
        headers={"X-Request-ID": request_id},
    )


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "service": "fastapi-monitoring-demo",
    }


@app.get("/users", tags=["API"])
async def users():
    return {
        "users": [
            {"id": 1, "name": "Aarav"},
            {"id": 2, "name": "Mira"},
            {"id": 3, "name": "Kabir"},
        ]
    }


@app.get("/products", tags=["API"])
async def products():
    return {
        "products": [
            {"id": 1, "name": "Laptop", "price": 79999},
            {"id": 2, "name": "Monitor", "price": 24999},
            {"id": 3, "name": "Keyboard", "price": 4999},
        ]
    }


async def validate_token(
    authorization: Annotated[str | None, Header()] = None,
):
    if authorization != "Bearer demo-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: invalid or missing bearer token",
        )
    return True


@app.get("/protected", tags=["Failure Simulation"])
async def protected(_: Annotated[bool, Depends(validate_token)]):
    return {
        "message": "Authenticated successfully",
        "user": "demo-user",
    }


@app.get("/simulate-error", tags=["Failure Simulation"])
async def simulate_error():
    # Intentional server failure for monitoring validation.
    raise RuntimeError("Intentional simulated server failure")


@app.get("/simulate-timeout", tags=["Failure Simulation"])
async def simulate_timeout():
    # Five seconds intentionally exceeds the 3-second alert threshold.
    await asyncio.sleep(5)
    return {
        "message": "Delayed response completed",
        "delay_seconds": 5,
    }


@app.get("/simulate-rate-limit", tags=["Failure Simulation"])
async def simulate_rate_limit():
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded: simulated for monitoring validation",
        headers={"Retry-After": "30"},
    )


Instrumentator(
    should_group_status_codes=False,
    excluded_handlers={"/metrics"},
).instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=True,
)
