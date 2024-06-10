from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from posts_app import models, oauth2, schemas
from posts_app.api.routers.deps import DBSessionDependency
from posts_app.utils import is_valid_password

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSessionDependency,
) -> schemas.Token:
    user = (
        db.query(models.User)
        .filter_by(email=user_credentials.username)
        .first()
    )

    if not user:
        raise HTTPException(
            detail="Invalid credentials",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not is_valid_password(
        plain_password=user_credentials.password,
        hashed_password=user.password,
    ):
        raise HTTPException(
            detail="Invalid credentials",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    access_token = oauth2.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    # trunk-ignore(bandit/B106)
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        expire_in=oauth2.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
