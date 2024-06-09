import json
import os

from faker import Faker
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


def get_dummy_data(count: int = 1000) -> list[dict]:
    fake = Faker()

    folks: list[dict] = []
    if os.path.exists("dummy_data.json"):
        with open("dummy_data.json", "r") as f:
            return json.load(f)

    for _ in range(count):
        data = {
            "id": fake.uuid4(),
            "name": fake.name(),
            "address": fake.address(),
            "email": fake.email(),
            "phone": fake.phone_number(),
        }
        folks.append(data)

    with open("dummy_data.json", "w") as f:
        json.dump(folks, f, indent=4)


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

            setattr(self, key, value)

        db.add(self)
        db.commit()
        db.refresh(self)
        return self