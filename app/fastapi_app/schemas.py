"""
Pydantic schemas for FastAPI request/response models.

Note: Most endpoints return raw SmartCover API responses (dict),
so we only define schemas for our custom auth endpoints.
"""
from pydantic import BaseModel, Field


# -------------------------
# Auth Schemas
# -------------------------
class TokenRequest(BaseModel):
    """Request body for authentication."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response from authentication endpoint."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token expiry in seconds")


class TokenInfoResponse(BaseModel):
    """Response from token info endpoint."""
    valid: bool
    username: str | None = None
    issued_at: str | None = None
    expires_at: str | None = None
    expires_in_seconds: int | None = None
    expires_in_human: str | None = None
    error: str | None = None
