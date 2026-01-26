import os
import json
from datetime import timedelta

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Default token limit per user (0 = unlimited)
DEFAULT_TOKEN_LIMIT = int(os.getenv("DEFAULT_TOKEN_LIMIT", "0"))

# API Users Configuration
# Can be set via environment variable as JSON or uses defaults
# Format: {"username": {"password": "xxx", "token_limit": 5, "enabled": true}}
def load_api_users() -> dict:
    """
    Load API users from API_USERS_JSON env var or fall back to simple admin config.

    JSON format:
    {
        "user1": {"password": "pass1", "token_limit": 5, "enabled": true},
        "user2": {"password": "pass2", "token_limit": 0, "enabled": true}
    }

    token_limit: 0 = unlimited, >0 = max active tokens allowed
    enabled: true/false to quickly disable a user
    """
    users_json = os.getenv("API_USERS_JSON")

    if users_json:
        try:
            return json.loads(users_json)
        except json.JSONDecodeError:
            print("Warning: Invalid API_USERS_JSON, falling back to default admin user")

    # Fallback to simple admin user from individual env vars
    return {
        "admin": {
            "password": os.getenv("API_ADMIN_PASSWORD", "admin123"),
            "token_limit": DEFAULT_TOKEN_LIMIT,
            "enabled": True,
        }
    }

API_USERS = load_api_users()
