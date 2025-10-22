from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from pwc.settings import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
security = HTTPBearer()


class TokenUser(BaseModel):
    """User information extracted from JWT token"""
    username: str
    user_id: str
    email: str
    is_active: bool


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


def create_access_token(user_data: Union[dict, Any], expires_delta: Optional[timedelta] = None):
    """Create JWT access token with enhanced user information"""
    # Handle both dict data and User objects
    if hasattr(user_data, 'username'):  # User object
        to_encode = {
            "sub": user_data.username,
            "user_id": str(user_data.id),
            "email": user_data.email,
            "is_active": user_data.is_active,
        }
    else:  # Legacy dict data
        to_encode = user_data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenUser:
    """Verify JWT token and return user information"""
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

        # Extract enhanced user information from token
        user_id = payload.get("user_id")
        email = payload.get("email")
        is_active = payload.get("is_active", True)

        # Handle legacy tokens that only have username
        if user_id is None:
            # For legacy tokens, we'll need to maintain backwards compatibility
            # but log a warning that enhanced tokens should be used
            return TokenUser(
                username=username,
                user_id="",  # Empty for legacy tokens
                email="",    # Empty for legacy tokens
                is_active=True  # Default for legacy tokens
            )

        return TokenUser(
            username=username,
            user_id=user_id,
            email=email,
            is_active=is_active
        )
    except JWTError:
        raise credentials_exception


# Dependency to get current user from token
async def get_current_user(token_user: TokenUser = Depends(verify_token)) -> TokenUser:
    """Get current authenticated user with full information from token"""
    if not token_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return token_user


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