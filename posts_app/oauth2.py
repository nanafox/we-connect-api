from datetime import datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from posts_app import models, schemas
from posts_app.api.routers.deps import DBSessionDependency
from posts_app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """Creates a JWT Access Token for API access."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=settings.secret_key,
        algorithm=settings.oauth2_algorithm,
    )
    settings.access_token_duration = expire
    return encoded_jwt


async def verify_access_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    credentials_exception: HTTPException,
) -> schemas.TokenData:
    """Verifies that the token being used is valid"""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.oauth2_algorithm]
        )
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None or email is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=user_id, email=email)
    except InvalidTokenError as error:
        raise credentials_exception from error

    return token_data


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: DBSessionDependency
) -> models.User:
    """Returns the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = await verify_access_token(token, credentials_exception)

    user = db.query(models.User).get(token_data.id)
    if not user:
        raise credentials_exception

    return user
