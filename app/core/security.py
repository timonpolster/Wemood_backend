import secrets
from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.jwt import verify_token

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def validate_api_key(
        api_key_header_val: str = Security(api_key_header),
) -> str:
    """Validiert den Admin-API-Key aus dem X-API-Key Header. Erlaubt Bypass im Dev-Modus."""
    admin_token = settings.ADMIN_API_KEY

    if not admin_token and settings.ENVIRONMENT == "dev":
        return "dev-bypass"

    if not admin_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Misconfiguration: ADMIN_API_KEY not set."
        )

    if not api_key_header_val:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing API Key. Please provide X-API-Key header."
        )

    if not secrets.compare_digest(api_key_header_val, admin_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key."
        )

    return api_key_header_val


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Extrahiert und validiert den aktuellen Benutzer aus dem JWT-Bearer-Token."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.sub
    if username is None:
        raise credentials_exception

    return username