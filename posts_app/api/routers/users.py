from fastapi import APIRouter, HTTPException, status

from posts_app import schemas
from posts_app.api.routers import CurrentUserDependency
from posts_app.api.routers.deps import (
    DBSessionDependency,
    QueryParamsDependency,
)
from posts_app.crud import crud_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[schemas.User],
    response_description="Users retrieved successfully",
)
async def get_users(
    query_params: QueryParamsDependency,
    db: DBSessionDependency,
):
    """Returns a list of users."""
    return crud_user.get_all(db=db, **query_params)


@router.get("/me", response_model=schemas.User)
async def get_current_user(
    current_user: CurrentUserDependency,
):
    """This endpoint returns the current user."""
    return current_user


@router.get(
    "/{user_id}",
    response_model=schemas.User,
    response_description="User retrieved successfully",
)
async def get_user(user_id: str, db: DBSessionDependency):
    return crud_user.get_by_id(db=db, id=user_id)


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: str,
    user: schemas.UserCreateUpdate,
    db: DBSessionDependency,
    current_user: CurrentUserDependency,
):
    return crud_user.update(
        db=db, schema=user, id=user_id, obj_owner_id=current_user.id
    )


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.User
)
async def create_user(
    user: schemas.UserCreateUpdate,
    db: DBSessionDependency,
    current_user: CurrentUserDependency,
):
    """This endpoint creates a new user."""
    if current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "This action is forbidden.",
                "reason": "You own an account already.",
            },
        )

    return crud_user.create(db=db, schema=user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str, db: DBSessionDependency, current_user: CurrentUserDependency
):
    """This endpoint deletes a user by its id."""
    return crud_user.delete(id=user_id, db=db, obj_owner_id=current_user.id)
