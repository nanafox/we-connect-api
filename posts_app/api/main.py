from dotenv import load_dotenv
from fastapi import FastAPI

from posts_app import models, schemas
from posts_app.api.routers import UserDependency, auth, posts, users
from posts_app.database import engine

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    servers=[{"url": "http://localhost:8000"}],
    title="Social Media App REST API",
    version="0.1.0",
    openapi_tags=[
        {"name": "Posts", "description": "Endpoints related to posts."},
        {"name": "Users", "description": "Endpoints related to users."},
        {
            "name": "Authentication",
            "description": "Endpoints related to authentication.",
        },
        {
            "name": "Status",
            "description": "Endpoint to check the API status.",
        },
    ],
    summary="This is a REST API for a social media app.",
    description="This REST API allows users to create, read, update, and delete posts and users.",
)

app.include_router(users.router, dependencies=[UserDependency])
app.include_router(posts.router, dependencies=[UserDependency])
app.include_router(auth.router)


@app.get(
    "/status",
    response_description="API status OK",
    response_model=schemas.StatusResponse,
    summary="API status",
    tags=["Status"],
)
def get_api_status():
    """This endpoint returns OK if the API server is up and running."""
    return {"status": "OK"}
