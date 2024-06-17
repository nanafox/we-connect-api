from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from posts_app import schemas
from posts_app.api.routers import UserDependency, auth, posts, users, votes
from posts_app.config import settings

load_dotenv()

if settings.dev:
    servers = {"url": "http://localhost:8000"}
else:
    servers = {"url": settings.production_server}

app = FastAPI(
    servers=[servers],
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
    summary="REST APIs for a simple social media app.",
    description="This REST API allows users to create, read, update, and "
    "delete posts and users.",
    redoc_url="/api/docs",
    docs_url="/api/interactive-docs",
)

# allow everyone for now
origins = ["*"]
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
router = APIRouter(prefix="/api")

router.include_router(users.router)
router.include_router(posts.router, dependencies=[UserDependency])
router.include_router(auth.router)
router.include_router(votes.router)


@router.get(
    "/status",
    response_description="API status OK",
    response_model=schemas.StatusResponse,
    summary="API status",
    tags=["Status"],
)
def get_api_status():
    """This endpoint returns OK if the API server is up and running."""
    return {"status": "OK"}


app.include_router(router)
