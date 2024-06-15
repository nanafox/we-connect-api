from fastapi import APIRouter, status

from posts_app import schemas
from posts_app.api.routers import CurrentUserDependency, UserDependency
from posts_app.api.routers.deps import DBSessionDependency
from posts_app.crud import crud_vote

router = APIRouter(
    prefix="/vote", tags=["Vote"], dependencies=[UserDependency]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_or_delete_vote(
    vote: schemas.Vote,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
) -> dict[str, str]:
    """This endpoint allows user to vote on a post."""
    return crud_vote.create_or_delete(
        db=db, vote=vote, user_id=current_user.id
    )
