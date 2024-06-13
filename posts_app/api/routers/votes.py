from fastapi import APIRouter, HTTPException, status

from posts_app import models, schemas
from posts_app.api.routers import CurrentUserDependency, UserDependency
from posts_app.api.routers.deps import DBSessionDependency

router = APIRouter(
    prefix="/vote", tags=["Vote"], dependencies=[UserDependency]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: schemas.Vote,
    current_user: CurrentUserDependency,
    db: DBSessionDependency,
):
    """This endpoint allows user to vote on a post."""
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id,
    )

    vote_found = vote_query.first()
    if vote.status:
        if vote_found:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can't vote on a post more than once.",
            )

        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()

        return {"message": "Vote added successfully"}
    else:
        if not vote_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote does not exist.",
            )

        vote_query.delete(synchronize_session=False)
        return {"message": "Vote deleted successfully"}
