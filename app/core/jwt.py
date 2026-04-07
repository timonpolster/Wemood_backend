from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from pydantic import BaseModel

from app.core.config import settings


class TokenPayload(BaseModel):
    """Struktur des dekodierten JWT-Payloads."""
    sub: str  # Subject
    exp: datetime  # Expiration time


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Erzeugt einen signierten JWT-Access-Token für den angegebenen Benutzer."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenPayload]:
    """Dekodiert und validiert einen JWT-Token. Gibt None zurück bei ungültigem Token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenPayload(**payload)
    except JWTError:
        return None