from datetime import datetime, timedelta, timezone
from typing import Annotated
import hashlib

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from .config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, API_USERS

security = HTTPBearer()

# In-memory token tracking (in production, use Redis or database)
# Format: {"username": {"token_hash": expiry_datetime, ...}}
_active_tokens: dict[str, dict[str, datetime]] = {}


def _hash_token(token: str) -> str:
    """Create a hash of the token for storage (don't store raw tokens)."""
    return hashlib.sha256(token.encode()).hexdigest()[:16]


def _cleanup_expired_tokens(username: str) -> None:
    """Remove expired tokens for a user."""
    if username not in _active_tokens:
        return

    now = datetime.now(timezone.utc)
    _active_tokens[username] = {
        token_hash: exp
        for token_hash, exp in _active_tokens[username].items()
        if exp > now
    }


def _count_active_tokens(username: str) -> int:
    """Count non-expired tokens for a user."""
    _cleanup_expired_tokens(username)
    return len(_active_tokens.get(username, {}))


def _register_token(username: str, token: str, expiry: datetime) -> None:
    """Register a new token for tracking."""
    if username not in _active_tokens:
        _active_tokens[username] = {}

    token_hash = _hash_token(token)
    _active_tokens[username][token_hash] = expiry


def get_user_config(username: str) -> dict | None:
    """Get user configuration dict."""
    user = API_USERS.get(username)
    if user is None:
        return None

    # Handle both old format (just password string) and new format (dict)
    if isinstance(user, str):
        return {"password": user, "token_limit": 0, "enabled": True}

    return user


def create_access_token(username: str) -> tuple[str, int]:
    """
    Create a JWT access token for the given username.

    Returns: (token, expires_in_seconds)
    Raises: HTTPException if token limit exceeded
    """
    user_config = get_user_config(username)
    if not user_config:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Check token limit
    token_limit = user_config.get("token_limit", 0)
    if token_limit > 0:
        active_count = _count_active_tokens(username)
        if active_count >= token_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Token limit reached. You have {active_count} active token(s). "
                       f"Maximum allowed: {token_limit}. Wait for existing tokens to expire.",
            )

    expires_delta = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = {
        "sub": username,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Track the token if limits are enabled
    if token_limit > 0:
        _register_token(username, encoded_jwt, expire)

    return encoded_jwt, int(expires_delta.total_seconds())


def verify_credentials(username: str, password: str) -> bool:
    """Verify username and password against stored credentials."""
    user_config = get_user_config(username)
    if user_config is None:
        return False

    # Check if user is enabled
    if not user_config.get("enabled", True):
        return False

    stored_password = user_config.get("password")
    if stored_password is None:
        return False

    # In production, use proper password hashing (bcrypt, argon2, etc.)
    return stored_password == password


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    """Dependency to validate JWT token and return current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_config = get_user_config(username)
    if user_config is None:
        raise credentials_exception

    # Check if user is still enabled
    if not user_config.get("enabled", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    return username


def get_token_info(token: str) -> dict:
    """
    Decode token and return info including expiry.

    Returns dict with: username, issued_at, expires_at, expires_in_seconds
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        exp_timestamp = payload.get("exp")
        iat_timestamp = payload.get("iat")
        username = payload.get("sub")

        now = datetime.now(timezone.utc)
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        issued_at = datetime.fromtimestamp(iat_timestamp, tz=timezone.utc) if iat_timestamp else None

        expires_in = expires_at - now
        expires_in_seconds = max(0, int(expires_in.total_seconds()))

        return {
            "valid": True,
            "username": username,
            "issued_at": issued_at.isoformat() if issued_at else None,
            "expires_at": expires_at.isoformat(),
            "expires_in_seconds": expires_in_seconds,
            "expires_in_human": _format_duration(expires_in_seconds),
        }
    except JWTError as e:
        return {
            "valid": False,
            "error": str(e),
        }


def _format_duration(seconds: int) -> str:
    """Format seconds into human readable duration."""
    if seconds <= 0:
        return "expired"

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")

    return " ".join(parts) if parts else "<1m"
