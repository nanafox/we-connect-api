from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas
from uuid import UUID


def get_post_by_id(db: Session, post_id: str):
    try:
        UUID(post_id)
    except ValueError:
        raise HTTPException(
            detail="invalid post id",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    else:
        post_data = (
            db.query(models.Post).filter(models.Post.id == post_id).first()
        )

    if post_data:
        return post_data

    raise HTTPException(
        detail="post not found", status_code=status.HTTP_404_NOT_FOUND
    )


def get_posts(db: Session, skip: int = 0, limit: int = 100) -> dict[str, list]:
    data = db.query(models.Post).offset(skip).limit(limit).all()
    return {"data": data}


def create_update_post(
    db: Session, post: schemas.PostCreateUpdate, post_id: str = None
):
    if post_id:
        new_post = get_post_by_id(db=db, post_id=post_id)
        for key, value in post.model_dump().items():
            setattr(new_post, key, value)
    else:
        new_post = models.Post(**post.model_dump())
        db.add(new_post)

    db.commit()
    db.refresh(new_post)
    return new_post


def delete_post(db: Session, post_id: str):
    post = get_post_by_id(db=db, post_id=post_id)

    db.delete(post)
    db.commit()
