
from fastapi import status, HTTPException, Depends, APIRouter, Response, status
from sqlalchemy.orm import Session

from app import oauth2
from ..schemas import schemas
from .. import models
from .. database import get_db


router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, response: Response,  db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    vote_query = db.query(models.Vote).filter(vote.post_id == models.Vote.post_id, current_user.id == models.Vote.user_id)

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

    if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post does not exist')

    found_vote = vote_query.first()

    if(vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'user {current_user.id} has already voted on post {vote.post_id}')
        
        new_vote = models.Vote(post_id = vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message":"successfully added vote"}
    else:
        vote_query.delete(synchronize_session=False)
        db.commit()
        response.status_code = status.HTTP_204_NO_CONTENT
        return{"message":"successfully deleted vote"}
        