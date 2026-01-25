import secrets
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def validate_api_key(
        api_key_header_val: str = Security(api_key_header),
) -> str:
    """
    Validates the API key from X-API-Key header.
    
    In development mode (ENVIRONMENT=dev), if ADMIN_API_KEY is not set,
    authentication is bypassed for convenience.
    
    In production mode, ADMIN_API_KEY must be set and all requests
    must include a valid X-API-Key header.
    """
    admin_token = settings.ADMIN_API_KEY
    
    # Dev bypass: Skip auth if no ADMIN_API_KEY is configured in dev environment
    if not admin_token and settings.ENVIRONMENT == "dev":
        return "dev-bypass"
    
    # Production check: ADMIN_API_KEY must be set
    if not admin_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Misconfiguration: ADMIN_API_KEY not set."
        )
    
    # Validate that header was provided
    if not api_key_header_val:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing API Key. Please provide X-API-Key header."
        )
    
    # Constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(api_key_header_val, admin_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key."
        )

    return api_key_header_val