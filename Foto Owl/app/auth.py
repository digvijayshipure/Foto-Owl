from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models
from .database import get_db

# Configuration for JWT and password hashing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")  # OAuth2 token endpoint URL
SECRET_KEY = "f7f8bc9e4b1147bfa31e7b2e9b965ba3a1c937a10f9dbfa2f925d19c04eb566b" # Secret key used for signing JWTs
ALGORITHM = "HS256"  # Algorithm used for JWT encoding
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Password hashing context


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hashed version.

    Parameter:
        plain_password: The plain text password.
        hashed_password: The hashed password.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    # Compare the plain password with the hashed password
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Parameter:
        password: The plain text password to hash.

    Returns:
        The hashed password.
    """
    # Generate a bcrypt hash of the password
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user by verifying email and password.

    Parameter:
        db: Database session dependency.
        email: The user's email address.
        password: The user's plain text password.

    Returns:
        The authenticated user object, or None if authentication fails.
    """
    # Retrieve the user from the database by email
    user = db.query(models.User).filter(models.User.email == email).first()
    
    # Verify the provided password matches the stored hash
    if not user or not verify_password(password, user.password):
        return None
    
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token.

    Parameter:
        data: Data to include in the token payload.
        expires_delta: Optional custom expiration duration.

    Returns:
        The encoded JWT token.
    """
    to_encode = data.copy()  # Copy the data to avoid mutating the input
    # Set the expiration time for the token
    expire = datetime.now() + expires_delta if expires_delta else timedelta(minutes=15)
    to_encode.update({"exp": expire})  # Add expiration time to the payload
    
    # Encode the token using the secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """
    Retrieve the current authenticated user from the JWT token.

    Parameter:
        token: The JWT token provided in the Authorization header.
        db: Database session dependency.

    Returns:
        The authenticated user object.

    Raises:
        If the token is invalid or the user does not exist.
    """
    # Exception to raise if token validation fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token to extract the payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")  # Extract the user ID from the "sub" claim
        if user_id is None:
            raise credentials_exception
    except JWTError:
        # Handle any errors during token decoding
        raise credentials_exception

    # Retrieve the user from the database using the extracted user ID
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception  # Raise exception if user is not found

    return user
