# flake8: noqa: B008

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session

from posts_app import crud, models, schemas
from posts_app.database import engine, get_db

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

crud_post = crud.APICrudBase[models.Post, schemas.Post](models.Post)

crud_user = crud.APICrudBase[models.User, schemas.User](models.User)


@app.get(
    "/status",
    response_description="API status OK",
    response_model=schemas.StatusResponse,
)
def get_api_status():
    """This endpoint returns OK if the API server is up and running."""
    return {"status": "OK"}


@app.get("/users", response_model=list[schemas.User])
async def get_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud_user.get_all(db=db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.User)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    return crud_user.get_by_id(db=db, id=user_id)


@app.put("/users/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: str,
    user: schemas.UserCreateUpdate,
    db: Session = Depends(get_db),
):
    return crud_user.update(db=db, schema=user, id=user_id)


@app.post(
    "/users", status_code=status.HTTP_201_CREATED, response_model=schemas.User
)
async def create_user(
    user: schemas.UserCreateUpdate, db: Session = Depends(get_db)
):
    return crud_user.create(db=db, schema=user)


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """This endpoint deletes a user by its id."""
    return crud_user.delete(id=user_id, db=db)


@app.get("/posts", response_model=schemas.PostsList)
async def get_posts(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    posts = crud_post.get_all(db=db, skip=skip, limit=limit)
    metadata = schemas.MetaData(
        links=schemas.Link(next=None, previous=None),
        status_code=status.HTTP_200_OK,
        count=len(posts),
        total_pages=1,
        current_page=1,
    )
    return {"data": posts, "metadata": metadata}


@app.get("/users/{user_id}/posts")
async def get_user_posts(user_id: str):
    return {"message": f"Posts of user {user_id}"}


@app.post(
    "/posts",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post,
)
async def create_post(
    post: schemas.PostCreateUpdate, db: Session = Depends(get_db)
):
    return crud_post.create(db=db, schema=post)


@app.get("/posts/{post_id}", response_model=schemas.Post)
async def get_post(post_id: str, db: Session = Depends(get_db)):
    """This endpoint returns a single post by its id."""
    return crud_post.get_by_id(db=db, id=post_id)


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: str, db: Session = Depends(get_db)):
    """This endpoint deletes a post by its id."""
    return crud_post.delete(post_id=post_id, db=db)


@app.put("/posts/{post_id}", response_model=schemas.Post)
async def update_post(
    post_id: str,
    post: schemas.PostCreateUpdate,
    db: Session = Depends(get_db),
):
    return crud_post.update(db=db, schema=post, id=post_id)


@app.patch("/posts/{post_id}", response_model=schemas.Post)
async def partial_update_post(
    post_id: str,
    post: schemas.PostPartialUpdate,
    db: Session = Depends(get_db),
):
    return crud_post.partial_update(db=db, schema=post, id=post_id)
