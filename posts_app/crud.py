from typing import Generic, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import Query, Session

from posts_app import models, schemas

ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class APICrudBase(Generic[ModelType, SchemaType]):
    def __init__(self, model: ModelType):
        self.model = model
        self.model_name = model.__name__.lower()

    @staticmethod
    def get_detailed_error(error: Exception):
        try:
            detail_error = error.args[0].split("\n")[1]
        except IndexError:
            return "The data provided is not correct"

        detail_error = detail_error.replace("DETAIL:  Key ", "")
        detail_error = (
            detail_error.replace("(", "").replace(")=", " ").replace(")", "")
        )
        detail_error = detail_error.replace('"', "'")
        return detail_error

    def get_by_id(self, *, db: Session, obj_id: str) -> ModelType:
        """Returns a single object by its id."""
        try:
            UUID(str(obj_id))
        except (ValueError, AttributeError) as error:
            print(error)
            raise HTTPException(
                detail=f"invalid {self.model_name} id",
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from error
        else:
            obj = db.query(self.model).filter(self.model.id == obj_id).first()

        if obj:
            return obj

        raise HTTPException(
            detail=f"{self.model_name} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    def get_all(self, *, db: Session, **query_fields) -> Query:
        """Return all objects of the model."""
        skip = query_fields.pop("skip", 0)
        limit = query_fields.pop("limit", 25)
        order_by = query_fields.pop("order_by", None)

        try:
            return (
                db.query(self.model)
                .order_by(order_by)
                .filter_by(**query_fields)
                .offset(skip)
                .limit(limit)
            )
        except Exception as error:
            raise HTTPException(
                detail={
                    "message": f"Error fetching {self.model_name} objects",
                    "reason": str(error).replace('"', "'"),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from error

    def create(
        self,
        db: Session,
        schema: SchemaType,
        obj_owner_id: str | None = None,
    ):
        try:
            if obj_owner_id:
                return self.model().save(
                    user_id=obj_owner_id, **schema.model_dump(), db=db
                )
            return self.model().save(**schema.model_dump(), db=db)
        except Exception as error:
            raise HTTPException(
                detail={
                    "message": f"Error creating {self.model_name}",
                    "reason": self.get_detailed_error(error),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from error

    def update(
        self,
        *,
        db: Session,
        schema: SchemaType,
        obj_id: str,
        obj_owner_id: str,
    ):
        obj = self.get_by_id(db=db, obj_id=obj_id)
        if not obj_owner_id == obj.id:
            raise HTTPException(
                detail="You are not authorized to update this "
                f"{self.model_name}",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        try:
            return obj.save(**schema.model_dump(), db=db)
        except Exception as error:
            raise HTTPException(
                detail={
                    "message": f"Error creating {self.model_name}",
                    "reason": self.get_detailed_error(error),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from error

    def delete(
        self,
        db: Session,
        obj_id: str,
        obj_owner_id: str,
    ):
        obj = self.get_by_id(db=db, obj_id=obj_id)
        if not obj_owner_id == obj.id:
            raise HTTPException(
                detail="You are not authorized to delete this "
                f"{self.model_name}",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        obj.delete(db=db)

    def partial_update(
        self,
        *,
        db: Session,
        schema: SchemaType,
        obj_id: str,
        obj_owner_id: str,
    ):
        stored_obj = self.get_by_id(obj_id=obj_id, db=db)
        if not obj_owner_id == stored_obj.id:
            raise HTTPException(
                detail=f"You are not authorized to update this "
                f"{self.model_name}",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        update_data = schema.model_dump(exclude_unset=True)
        return stored_obj.save(**update_data, db=db)


class PostCrud(APICrudBase[models.Post, schemas.Post]):
    """CRUD operations for the Post model."""

    def __init__(self, model: models.Post = models.Post):
        super().__init__(model)

    def update(
        self,
        *,
        db: Session,
        schema: schemas.PostCreateUpdate,
        post_id: str,
        user_id: str,
    ):
        """Update a post."""
        post = self.get_by_id(db=db, post_id=post_id)[0]
        if not user_id == post.user_id:
            raise HTTPException(
                detail="You are not authorized to update this post",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return post.save(**schema.model_dump(), db=db)

    def delete(
        self,
        db: Session,
        post_id: str,
        user_id: str,
    ):
        """Delete a post."""
        post = self.get_by_id(db=db, post_id=post_id)[0]
        if not user_id == post.user_id:
            raise HTTPException(
                detail="You are not authorized to delete this post",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        post.delete(db=db)

    def partial_update(
        self,
        *,
        db: Session,
        schema: schemas.PostPartialUpdate,
        post_id: str,
        user_id: str,
    ):
        """Partially update a post."""
        stored_post = self.get_by_id(post_id=post_id, db=db)[0]
        if not user_id == stored_post.user_id:
            raise HTTPException(
                detail="You are not authorized to update this post",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        update_data = schema.model_dump(exclude_unset=True)
        return stored_post.save(**update_data, db=db)

    def get_all(self, *, db: Session, **query_fields) -> Query:
        """
        Get all posts.

        This can be further filtered by passing query parameters.
        """
        skip = query_fields.pop("skip", 0)
        limit = query_fields.pop("limit", 25)
        order_by = query_fields.pop("order_by", None)
        search = query_fields.pop("search", "")

        try:
            results = (
                db.query(
                    self.model, func.count(models.Vote.post_id).label("votes")
                )
                .filter(
                    or_(
                        self.model.title.icontains(search),
                        self.model.content.icontains(search),
                    )
                )
                .filter_by(**query_fields)
                .outerjoin(models.Vote, models.Vote.post_id == self.model.id)
                .group_by(self.model.id)
                .order_by(order_by)
                .offset(skip)
                .limit(limit)
            )
        except Exception as error:
            raise HTTPException(
                detail={
                    "message": "Error fetching posts",
                    "reason": str(error).replace('"', "'"),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from error
        else:
            return results

    def get_by_id(
        self, *, db: Session, post_id: str
    ) -> Row[tuple[models.Post, int]]:
        """Returns a single post by its id."""
        try:
            UUID(str(post_id))
        except (ValueError, AttributeError) as error:
            raise HTTPException(
                detail="invalid post id",
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from error
        else:
            data: Row = (
                db.query(
                    self.model, func.count(models.Vote.post_id).label("votes")
                )
                .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
                .group_by(models.Post.id)
                .filter(models.Post.id == post_id)
                .first()
            )

        if not data:
            raise HTTPException(
                detail="Post not found", status_code=status.HTTP_404_NOT_FOUND
            )

        return data


class VoteCrud(APICrudBase[models.Vote, schemas.Vote]):
    def __init__(self, model: models.Vote = models.Vote):
        super().__init__(model)

    def create_or_delete(
        self, db: Session, vote: schemas.Vote, user_id: str
    ) -> dict[str, str]:
        """Adds or removes a vote from post."""
        vote_found = (
            db.query(models.Vote)
            .filter(
                models.Vote.post_id == vote.post_id,
                models.Vote.user_id == user_id,
            )
            .first()
        )

        # ensure the post exists before moving forward
        PostCrud().get_by_id(db=db, post_id=str(vote.post_id))

        if vote.status:
            if vote_found:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already voted on this post",
                )
            try:
                self.create(db=db, schema=vote, obj_owner_id=user_id)
            except Exception as error:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Error creating vote",
                        "reason": self.get_detailed_error(error),
                    },
                ) from error
            return {"message": "Vote added successfully"}
        else:
            if not vote_found:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vote does not exist.",
                )

            vote_found.delete(db=db)
            return {"message": "Vote deleted successfully"}


crud_user = APICrudBase[models.User, schemas.User](models.User)
crud_post = PostCrud()
crud_vote = VoteCrud()
