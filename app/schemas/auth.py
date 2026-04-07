from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    """Eingabeschema für Login-Anfragen."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    """Antwortschema mit JWT-Access-Token nach erfolgreichem Login."""
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    """Antwortschema mit öffentlichen Benutzerinformationen."""
    username: str
    is_active: bool