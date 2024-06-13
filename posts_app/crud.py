from typing import Generic, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from posts_app import models, schemas

ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class APICrudBase(Generic[ModelType, SchemaType]):
    def __init__(self, model: ModelType):
        self.model = model
        self.model_name = model.__name__

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
        return detail_error

    def get_by_id(self, *, db: Session, id: str) -> ModelType:
        try:
            UUID(id)
        except ValueError as error:
            raise HTTPException(
                detail=f"invalid {self.model_name} id",
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from error
        else:
            obj = db.query(self.model).filter(self.model.id == id).first()

        if obj:
            return obj

        raise HTTPException(
            detail=f"{self.model_name} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    def get_all(self, *, db: Session, **search_fields) -> list[ModelType]:
        skip = search_fields.pop("skip", 0)
        limit = search_fields.pop("limit", 100)
        order_by = search_fields.pop("order_by", None)

        try:
            return (
                db.query(self.model)
                .order_by(order_by)
                .filter_by(**search_fields)
                .offset(skip)
                .limit(limit)
                .all()
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
        id: str,
        obj_owner_id: str,
    ):
        obj = self.get_by_id(db=db, id=id)
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
        id: str,
        obj_owner_id: str,
    ):
        obj = self.get_by_id(db=db, id=id)
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
        id: str,
        obj_owner_id: str,
    ):
        stored_obj = self.get_by_id(id=id, db=db)
        if not obj_owner_id == stored_obj.id:
            raise HTTPException(
                detail=f"You are not authorized to update this "
                f"{self.model_name}",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        update_data = schema.model_dump(exclude_unset=True)
        return stored_obj.save(**update_data, db=db)


class PostCRUD(APICrudBase[models.Post, schemas.Post]):
    def update(
        self,
        *,
        db: Session,
        schema: schemas.PostCreateUpdate,
        id: str,
        obj_owner_id: str,
    ):
        obj = self.get_by_id(db=db, id=id)
        if not obj_owner_id == obj.user_id:
            raise HTTPException(
                detail="You are not authorized to update this post",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return obj.save(**schema.model_dump(), db=db)

    def delete(
        self,
        db: Session,
        id: str,
        obj_owner_id: str,
    ):
        obj = self.get_by_id(db=db, id=id)
        if not obj_owner_id == obj.user_id:
            raise HTTPException(
                detail="You are not authorized to delete this post",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        obj.delete(db=db)

    def partial_update(
        self,
        *,
        db: Session,
        schema: schemas.PostPartialUpdate,
        id: str,
        obj_owner_id: str,
    ):
        stored_obj = self.get_by_id(id=id, db=db)
        if not obj_owner_id == stored_obj.user_id:
            raise HTTPException(
                detail="You are not authorized to update this post",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        update_data = schema.model_dump(exclude_unset=True)
        return stored_obj.save(**update_data, db=db)


crud_user = APICrudBase[models.User, schemas.User](models.User)
crud_post = PostCRUD(models.Post)
