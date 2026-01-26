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
    api_name: str = Field(description="API identifier (API_1, API_2, etc.)")


class TokenInfoResponse(BaseModel):
    """Response from token info endpoint."""
    valid: bool
    username: str | None = None
    api_name: str | None = None
    issued_at: str | None = None
    expires_at: str | None = None
    expires_in_seconds: int | None = None
    expires_in_human: str | None = None
    error: str | None = None


class TokenStatusResponse(BaseModel):
    """Response showing user's token usage status."""
    username: str
    active_tokens: int
    token_limit: int | str = Field(description="Token limit or 'unlimited'")
    remaining: int | str = Field(description="Remaining tokens or 'unlimited'")


class UserTokenInfo(BaseModel):
    """Info about a single user token."""
    api_name: str
    token: str = Field(description="The JWT access token")
    created_at: str
    expires_at: str
    expires_in_seconds: int
    expires_in_human: str


class UserTokensResponse(BaseModel):
    """Response listing all user's active tokens."""
    username: str
    tokens: list[UserTokenInfo]
