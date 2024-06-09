# flake8: noqa: B008

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from posts_app import crud, models, schemas
from posts_app.database import get_db
from posts_app.utils import get_query_params

router = APIRouter(prefix="/users", tags=["Users"])

crud_user = crud.APICrudBase[models.User, schemas.User](models.User)


@router.get(
    "/",
    response_model=list[schemas.User],
    response_description="Users retrieved successfully",
)
async def get_users(
    db: Session = Depends(get_db),
    query_params: dict = Depends(get_query_params),
):
    """Returns a list of users."""
    return crud_user.get_all(db=db, **query_params)


@router.get(
    "/{user_id}",
    response_model=schemas.User,
    response_description="User retrieved successfully",
)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    return crud_user.get_by_id(db=db, id=user_id)


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: str,
    user: schemas.UserCreateUpdate,
    db: Session = Depends(get_db),
):
    return crud_user.update(db=db, schema=user, id=user_id)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.User
)
async def create_user(
    user: schemas.UserCreateUpdate, db: Session = Depends(get_db)
):
    return crud_user.create(db=db, schema=user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """This endpoint deletes a user by its id."""
    return crud_user.delete(id=user_id, db=db)
