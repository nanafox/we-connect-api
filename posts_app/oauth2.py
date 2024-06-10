import os
from datetime import datetime, timedelta
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from posts_app import models, schemas
from posts_app.api.routers.deps import DBSessionDependency

load_dotenv()


SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


async def verify_access_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    credentials_exception: HTTPException,
) -> schemas.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("sub")
        email = payload.get("email")
        if id is None or email is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id, email=email)
    except InvalidTokenError:
        raise credentials_exception

    return token_data


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: DBSessionDependency
) -> schemas.TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = await verify_access_token(token, credentials_exception)

    return db.query(models.User).get(token_data.id)
