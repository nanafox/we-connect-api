from typing import Generic, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class APICrudBase(Generic[ModelType, SchemaType]):
    def __init__(self, model: ModelType):
        self.model = model
        self.model_name = model.__name__

    @staticmethod
    def get_detailed_error(error: Exception):
        detail_error = error.args[0].split("\n")[1]
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

    def get_all(self, *, db: Session, skip: int = 0, limit: int = 100):
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, schema: SchemaType):
        try:
            return self.model(**schema.model_dump()).save(db=db)
        except Exception as error:
            raise HTTPException(
                detail={
                    "message": f"Error creating {self.model_name}",
                    "reason": self.get_detailed_error(error),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from error

    def update(self, *, db: Session, schema: SchemaType, id: str):
        obj = self.get_by_id(db=db, id=id)
        return obj.save(**schema.model_dump(), db=db)

    def delete(self, db: Session, id: str):
        obj = self.get_by_id(db=db, id=id)

        db.delete(obj)
        db.commit()

    def partial_update(self, *, db: Session, schema: SchemaType, id: str):
        stored_obj = self.get_by_id(id=id, db=db)
        update_data = schema.model_dump(exclude_unset=True)
        return stored_obj.save(**update_data, db=db)