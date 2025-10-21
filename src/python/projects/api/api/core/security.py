from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pwc.settings import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Truncate password to 72 bytes for bcrypt compatibility
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Truncate password to 72 bytes for bcrypt compatibility
    # bcrypt only considers the first 72 bytes anyway
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token and return username"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


# Dependency to get current user from token
async def get_current_user(username: str = Depends(verify_token)) -> str:
    """Get current authenticated user"""
    # In a real app, you'd fetch user from database
    # For now, just return the username
    return username


def generate_internal_token() -> str:
    """Generate a JWT token for internal worker communication"""
    data = {
        "sub": "internal_worker",
        "type": "internal",
        "iss": "pwc_api"
    }
    return create_access_token(data, expires_delta=timedelta(hours=24))


def verify_internal_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token for internal worker access"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid internal token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        token_type = payload.get("type")
        issuer = payload.get("iss")

        if token_type != "internal" or issuer != "pwc_api":
            raise credentials_exception

        return payload.get("sub", "internal_worker")
    except JWTError:
        raise credentials_exception