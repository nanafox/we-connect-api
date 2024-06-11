from fastapi import APIRouter, status

from posts_app import schemas
from posts_app.api.routers import CurrentUserDependency
from posts_app.api.routers.deps import DBSessionDependency, QueryParamsDependency
from posts_app.crud import crud_post

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=schemas.PostsList)
async def get_posts(
    query_params: QueryParamsDependency,
    db: DBSessionDependency,
):
    posts = crud_post.get_all(db=db, **query_params)

    metadata = schemas.MetaData(
        links=schemas.Link(next=None, previous=None),
        status_code=status.HTTP_200_OK,
        count=len(posts),
        total_pages=1,
        current_page=1,
    )
    return {"data": posts, "metadata": metadata}


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
    return crud_post.create(db=db, schema=post, obj_owner_id=user.id)


@router.get("/{post_id}", response_model=schemas.Post)
async def get_post(post_id: str, db: DBSessionDependency):
    """This endpoint returns a single post by its id."""
    return crud_post.get_by_id(db=db, id=post_id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str, db: DBSessionDependency, user: CurrentUserDependency
):
    """This endpoint deletes a post by its id."""
    return crud_post.delete(id=post_id, db=db, obj_owner_id=user.id)


@router.put("/{post_id}", response_model=schemas.Post)
async def update_post(
    post_id: str,
    post: schemas.PostCreateUpdate,
    db: DBSessionDependency,
    user: CurrentUserDependency,
):
    return crud_post.update(
        db=db, schema=post, id=post_id, obj_owner_id=user.id
    )


@router.patch("/{post_id}", response_model=schemas.Post)
async def partial_update_post(
    post_id: str,
    post: schemas.PostPartialUpdate,
    db: DBSessionDependency,
    user: CurrentUserDependency,
):
    return crud_post.partial_update(
        db=db, schema=post, id=post_id, obj_owner_id=user.id
    )
