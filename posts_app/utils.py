from fastapi import HTTPException, Request, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UtilMixin:
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def save(self, db: Session, **kwargs):
        """Saves or updates the post object."""
        for key, value in kwargs.items():
            if value is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": f"Invalid value passed as {key}.",
                        "next_steps": "Verify you provided the right data.",
                    },
                )
            if key == "password":
                value = pwd_context.hash(value)

            setattr(self, key, value)

        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session):
        """Deletes the post object."""
        db.delete(self)
        db.commit()


def get_query_params(request: Request):
    return request.query_params


def is_valid_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
