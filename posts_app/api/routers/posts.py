# flake8: noqa: B008

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from posts_app import crud, models, schemas
from posts_app.database import get_db
from posts_app.utils import get_query_params

router = APIRouter(prefix="/posts", tags=["Posts"])

crud_post = crud.APICrudBase[models.Post, schemas.Post](models.Post)


@router.get("/", response_model=schemas.PostsList)
async def get_posts(
    db: Session = Depends(get_db),
    query_params: dict = Depends(get_query_params),
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


@router.get("/{user_id}/posts")
async def get_user_posts(user_id: str):
    return {"message": f"Posts of user {user_id}"}


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post,
)
async def create_post(
    post: schemas.PostCreateUpdate, db: Session = Depends(get_db)
):
    return crud_post.create(db=db, schema=post)


@router.get("/{post_id}", response_model=schemas.Post)
async def get_post(post_id: str, db: Session = Depends(get_db)):
    """This endpoint returns a single post by its id."""
    return crud_post.get_by_id(db=db, id=post_id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: str, db: Session = Depends(get_db)):
    """This endpoint deletes a post by its id."""
    return crud_post.delete(post_id=post_id, db=db)


@router.put("/{post_id}", response_model=schemas.Post)
async def update_post(
    post_id: str,
    post: schemas.PostCreateUpdate,
    db: Session = Depends(get_db),
):
    return crud_post.update(db=db, schema=post, id=post_id)


@router.patch("/{post_id}", response_model=schemas.Post)
async def partial_update_post(
    post_id: str,
    post: schemas.PostPartialUpdate,
    db: Session = Depends(get_db),
):
    return crud_post.partial_update(db=db, schema=post, id=post_id)
