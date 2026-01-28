from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, username: str, password: str) -> User:
        hashed_password = pwd_context.hash(password)
        user = User(
            username=username,
            hashed_password=hashed_password,
            is_active=True
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        user = await self.get_by_username(username)
        if not user:
            return None
        if not await self.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
