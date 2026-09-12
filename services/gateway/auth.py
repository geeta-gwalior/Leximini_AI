import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from services.gateway.config import settings
from services.gateway.database import get_db
from services.gateway.models import User

logger = logging.getLogger("leximini.auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# NOTE: OAuth2 scheme auto_error=False allows public guest routes to pass gracefully
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not token:
        # Guest request context (unauthenticated)
        return None
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("JWT payload missing 'sub' claim")
            raise credentials_exception
    except JWTError as err:
        logger.debug(f"JWT decode failure: {err}")
        raise credentials_exception

    # TODO: Add Redis token revocation check here for enterprise instant logout
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user is None:
        logger.warning(f"Valid token presented for non-existent user: {email}")
        raise credentials_exception
    return user

async def get_current_org_admin(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required for organization admin actions.")
    if current_user.role != "COMPANY_ADMIN":
        logger.warning(f"Forbidden access attempt by user {current_user.email} (Role: {current_user.role})")
        raise HTTPException(status_code=403, detail="Company Admin privileges required for this action.")
    return current_user


