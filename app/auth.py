"""Autenticação (JWT) e autorização por papel (RBAC)."""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.database import get_session
from app.models import Role, User

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# pbkdf2_sha256 é puro-Python: evita dependências nativas (bcrypt) no Windows/CI.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    user = session.exec(select(User).where(User.username == username)).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except jwt.PyJWTError:
        raise credentials_error
    if username is None:
        raise credentials_error

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_error
    return user


def require_roles(*roles: Role):
    """Fábrica de dependência: exige que o usuário tenha um dos papéis dados."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado: requer papel {[r.value for r in roles]}",
            )
        return user

    return checker
