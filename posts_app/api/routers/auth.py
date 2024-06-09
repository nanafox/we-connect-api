# flake8: noqa: B008


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from posts_app import crud, models, schemas
from posts_app.database import get_db
from posts_app.utils import is_valid_password

router = APIRouter(tags=["Authentication"])

crud_user = crud.APICrudBase[models.User, schemas.User](models.User)


@router.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud_user.get_all(db=db, email=user_credentials.email)[0]
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Credentials",
        )

    if not is_valid_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Credentials",
        )
    return {"message": "Successfully logged in"}
