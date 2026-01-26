import json
import logging
import os
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

from .routes import router
from .config import JWT_SECRET_KEY, JWT_ALGORITHM

# Configure logging with timestamps - both console and file
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create logger
logger = logging.getLogger("smartcover_api")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
logger.addHandler(console_handler)

# File handler (persistent logs with rotation)
LOG_DIR = "/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = RotatingFileHandler(
    f"{LOG_DIR}/api_access.log",
    maxBytes=10_000_000,  # 10MB per file
    backupCount=5,  # Keep 5 backup files
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
logger.addHandler(file_handler)

# JSON log file path
JSON_LOG_FILE = f"{LOG_DIR}/api_requests.json"


def append_json_log(log_entry: dict):
    """Append a log entry to the JSON log file."""
    try:
        # Read existing logs
        if os.path.exists(JSON_LOG_FILE):
            with open(JSON_LOG_FILE, "r") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        # Append new entry
        logs.append(log_entry)

        # Keep last 10000 entries to prevent file from growing too large
        if len(logs) > 10000:
            logs = logs[-10000:]

        # Write back
        with open(JSON_LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to write JSON log: {e}")

app = FastAPI(
    title="SmartCover Proxy API",
    description="""
## SmartCover Data Proxy Service

This API provides authenticated access to SmartCover IoT sensor data.

### Authentication
1. Call `POST /api/v1/auth/token` with your credentials
2. Use the returned JWT token in the `Authorization` header: `Bearer <token>`

### Available Endpoints
- **Locations**: Get monitoring site information
- **Live Data**: Real-time sensor readings
- **Historical Data**: Time-series data queries
- **Alarms**: Alarm events and status
- **Alerts**: Alert events and status
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - configure as needed for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware class to capture request body
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Extract username from JWT token if present
        username = "anonymous"
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                username = payload.get("sub", "unknown")
            except Exception:
                username = "invalid_token"

        # Capture request body for POST/PUT/PATCH
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        request_body = json.loads(body_bytes.decode("utf-8"))
                        # Mask password fields for security
                        if isinstance(request_body, dict) and "password" in request_body:
                            request_body["password"] = "***MASKED***"
                    except json.JSONDecodeError:
                        request_body = body_bytes.decode("utf-8", errors="replace")
            except Exception:
                request_body = None

        # Get query parameters
        query_params = dict(request.query_params) if request.query_params else None

        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Console/text log
        logger.info(
            f"user={username} | ip={client_ip} | {request.method} {request.url.path} | "
            f"status={response.status_code} | {duration_ms:.1f}ms"
        )

        # JSON log with full details
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": username,
            "ip": client_ip,
            "method": request.method,
            "path": request.url.path,
            "query_params": query_params,
            "request_body": request_body,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "user_agent": request.headers.get("User-Agent", "unknown"),
        }
        append_json_log(log_entry)

        return response


app.add_middleware(LoggingMiddleware)


# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "SmartCover Proxy API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
