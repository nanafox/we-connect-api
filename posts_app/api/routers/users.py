from fastapi import APIRouter, HTTPException, Request, status

from posts_app import oauth2, schemas
from posts_app.api.routers import CurrentUserDependency, UserDependency
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
    dependencies=[UserDependency],
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
    dependencies=[UserDependency],
)
async def get_user(user_id: str, db: DBSessionDependency):
    return crud_user.get_by_id(db=db, obj_id=user_id)


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: str,
    user: schemas.UserCreateUpdate,
    db: DBSessionDependency,
    current_user: CurrentUserDependency,
):
    return crud_user.update(
        db=db, schema=user, obj_id=user_id, obj_owner_id=current_user.id
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.User,
)
async def create_user(
    user: schemas.UserCreateUpdate,
    db: DBSessionDependency,
    request: Request,
):
    """This endpoint creates a new user."""
    data = dict(request.headers._list)
    bearer_token = data.get("authorization", None)

    # let's verify if the bearer token was set, it shouldn't be set when
    # creating  a user
    if bearer_token:
        try:
            user = oauth2.get_current_user(token=bearer_token, db=db)
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Don't set the authorization header "
                "when creating a user.",
            ) from error
        else:
            # this is an authenticated user trying to create a user, this
            # shouldn't be allowed.
            if user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to create a user.",
                )

    return crud_user.create(db=db, schema=user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str, db: DBSessionDependency, current_user: CurrentUserDependency
):
    """This endpoint deletes a user by its id."""
    return crud_user.delete(
        obj_id=user_id, db=db, obj_owner_id=current_user.id
    )
