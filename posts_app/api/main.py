# flake8: noqa: B008

from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from posts_app import crud, models, schemas
from posts_app.database import engine, get_db
from posts_app.utils import get_dummy_data

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

folks_data = get_dummy_data()


@app.get("/")
def root():
    return {"message": "Welcome to the API"}


@app.get("/status")
def get_status():
    """This endpoint returns OK if the API server is up and running."""
    return {"status": "OK"}


@app.get("/users")
async def get_users(skip: int = 0, limit: int = 25):
    data = folks_data[skip : skip + limit]
    return {"count": len(data), "data": data}


@app.get("/users/{user_id}")
async def get_user(user_id: str) -> dict[str, Any]:
    for user_data in folks_data:
        if user_data["id"] == user_id:
            return user_data

    raise HTTPException(detail="user not found", status_code=404)


@app.get("/posts", response_model=schemas.PostsList)
async def get_posts(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    posts = crud.get_posts(db=db, skip=skip, limit=limit)
    metadata = schemas.MetaData(
        links=schemas.Link(next=None, previous=None),
        status_code=status.HTTP_200_OK,
        count=len(posts),
        total_pages=1,
        current_page=1,
    )
    return {"data": posts, "metadata": metadata}


@app.get("/users/{user_id}/posts")
def get_user_posts(user_id: str):
    return {"message": f"Posts of user {user_id}"}


@app.post(
    "/posts",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post,
)
async def create_post(
    data: schemas.PostCreateUpdate, db: Session = Depends(get_db)
):
    return crud.create_update_post(db=db, post=data)


@app.get("/posts/{post_id}", response_model=schemas.Post)
async def get_post(post_id: str, db: Session = Depends(get_db)):
    """This endpoint returns a single post by its id."""
    return crud.get_post_by_id(db=db, post_id=post_id)


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: str, db: Session = Depends(get_db)):
    """This endpoint deletes a post by its id."""
    return crud.delete_post(post_id=post_id, db=db)


@app.put("/posts/{post_id}", response_model=schemas.Post)
async def update_post(
    post_id: str,
    data: schemas.PostCreateUpdate,
    db: Session = Depends(get_db),
):
    return crud.create_update_post(db=db, post=data, post_id=post_id)


@app.patch("/posts/{post_id}", response_model=schemas.Post)
async def partial_update_post(
    post_id: str,
    post: schemas.PostPartialUpdate,
    db: Session = Depends(get_db),
):
    return crud.partial_post_update(db=db, post=post, post_id=post_id)



@app.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return {"message": "User created successfully"}
