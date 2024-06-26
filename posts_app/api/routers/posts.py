from typing import Any

from fastapi import APIRouter, status

from posts_app import schemas
from posts_app.api.routers import CurrentUserDependency
from posts_app.api.routers.deps import (
    DBSessionDependency,
    QueryParamsDependency,
)
from posts_app.crud import crud_post
from posts_app.schemas import MetaData

router = APIRouter(prefix="/posts", tags=["Posts"])


def get_post_data(posts_data: list[tuple]) -> list[dict[str, Any]]:
    """Returns the data for the posts."""
    data = []
    for post, votes in posts_data:
        data.append(
            {
                "post": post,
                "votes": votes,
            }
        )
    return data


@router.get("/", response_model=schemas.PostsList)
async def get_posts(
    query_params: QueryParamsDependency,
    db: DBSessionDependency,
) -> dict[str, list[dict[str, Any]] | MetaData]:
    """Retrieves all the posts created by current active users."""
    posts_data = crud_post.get_all(db=db, **query_params)

    data = get_post_data(posts_data)

    metadata = schemas.MetaData(
        links=schemas.Link(next=None, previous=None),
        status_code=status.HTTP_200_OK,
        count=len(data),
        total_pages=1,
        current_page=1,
    )

    return {"data": data, "metadata": metadata}


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post,
)
async def create_post(
    post: schemas.PostCreateUpdate,
    db: DBSessionDependency,
    user: CurrentUserDependency,
) -> schemas.Post:
    """This endpoint creates a post for the authenticated user."""
    return crud_post.create(db=db, schema=post, obj_owner_id=user.id)


@router.get("/me", response_model=list[schemas.PostResponse])
async def get_current_user_posts(
    db: DBSessionDependency,
    user: CurrentUserDependency,
) -> list[dict[str, Any]]:
    """
    This endpoint retrieves all the posts for the current authenticated
    user.
    """
    return get_post_data(crud_post.get_all(db=db, **{"user_id": user.id}))


@router.get("/{post_id}", response_model=schemas.PostResponse)
async def get_post(post_id: str, db: DBSessionDependency):
    """This endpoint returns a single post by its id."""
    post, votes = crud_post.get_by_id(db=db, post_id=post_id)

    return {"post": post, "votes": votes}


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str, db: DBSessionDependency, user: CurrentUserDependency
):
    """This endpoint deletes a post by its id."""
    return crud_post.delete(obj_id=post_id, db=db, obj_owner_id=user.id)


@router.put("/{post_id}", response_model=schemas.Post)
async def update_post(
    post_id: str,
    post: schemas.PostCreateUpdate,
    db: DBSessionDependency,
    user: CurrentUserDependency,
):
    """Updates a post."""
    return crud_post.update(
        db=db, schema=post, post_id=post_id, user_id=user.id
    )


@router.patch("/{post_id}", response_model=schemas.Post)
async def partial_update_post(
    post_id: str,
    post: schemas.PostPartialUpdate,
    db: DBSessionDependency,
    user: CurrentUserDependency,
):
    """Partially updates a user's post."""
    return crud_post.partial_update(
        db=db, schema=post, id=post_id, obj_owner_id=user.id
    )
