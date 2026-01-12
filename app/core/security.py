import os
import secrets
from typing import Optional
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def validate_api_key(
        api_key_header_val: str = Security(api_key_header),
) -> str:
    if not api_key_header_val:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )

    admin_token = getattr(settings, "ADMIN_API_KEY", None)

    if not admin_token:
        admin_token = os.getenv("ADMIN_API_KEY")

    if not admin_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Misconfiguration: ADMIN_API_KEY not set."
        )

    if not secrets.compare_digest(api_key_header_val, admin_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )

    return api_key_header_val