from typing import Generic
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from posts_app import models, schemas


def get_post_by_id(db: Session, post_id: str) -> models.Post:
    """
    Returns the post that matches the specified id.

    Args:
        db (Session): The database session (connection) to use.
        post_id (str): The id of the post to retrieve.

    Raises:
        HTTPException: If the id provided was invalid or matched nothing.

    Returns:
        models.Post: The post object if it was matched.
    """
    try:
        UUID(post_id)
    except ValueError as error:
        raise HTTPException(
            detail="invalid post id",
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from error
    else:
        post_data = (
            db.query(models.Post).filter(models.Post.id == post_id).first()
        )

    if post_data:
        return post_data

    raise HTTPException(
        detail="post not found", status_code=status.HTTP_404_NOT_FOUND
    )


def get_posts(
    db: Session, skip: int = 0, limit: int = 100
) -> list[schemas.Post]:
    """
    Retrieves all post

    Args:
        db (Session): The database session (connection) to use.
        skip (int, optional): The offset to start from. Defaults to 0.
        limit (int, optional): The upper bound limit of objects to return.
        Defaults to 100.

    Returns:
        list[schemas.Post]: A list of post objects
    """
    return db.query(models.Post).offset(skip).limit(limit).all()


def create_update_post(
    db: Session, post: schemas.PostCreateUpdate, post_id: str = None
) -> models.Post:
    """
    Creates or updates a post.

    Args:
        db (Session): The database session (connection) to use.
        post (schemas.PostCreateUpdate): The post object schema.
        post_id (str, optional): The id of the post to update. This is only
        required for updates (PUT requests). Defaults to None.

    Returns:
        models.Post: The created or the updated post.
    """
    if post_id:
        new_post = get_post_by_id(db=db, post_id=post_id)
    else:
        new_post = models.Post(**post.model_dump())

    return new_post.save(**post.model_dump(), db=db)


def delete_post(db: Session, post_id: str):
    """
    Deletes a post.

    Args:
        db (Session): The database session (connection) to use.
        post_id (str): The id of the post to delete.
    """
    post = get_post_by_id(db=db, post_id=post_id)

    db.delete(post)
    db.commit()


def partial_post_update(
    db: Session, post: schemas.PostPartialUpdate, post_id: str
) -> models.Post:
    """
    Partially updates a post object.

    This is useful when performing PATCH requests on the API endpoint.

    Args:
        db (Session): The database session (connection) to use.
        post (schemas.PostPartialUpdate): The schema of the post object.
        post_id (str): The id of the post to be updated.

    Returns:
        models.Post: The updated post.
    """
    stored_post = get_post_by_id(post_id=post_id, db=db)
    update_data = post.model_dump(exclude_unset=True)
    return stored_post.save(**update_data, db=db)
