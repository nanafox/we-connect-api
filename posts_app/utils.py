import json
import os

from faker import Faker


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
