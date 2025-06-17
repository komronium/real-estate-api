from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.comment import CommentCreate, CommentOut
from app.services.comment_service import CommentService
from app.api.deps import get_db, get_current_user

router = APIRouter(prefix="/api/v1", tags=["Comments"])


@router.post("/ads/{ad_id}/comments/", response_model=CommentOut)
def create_comment_for_ad(
    ad_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CommentService(db)
    return service.create_comment(ad_id=ad_id, user_id=current_user.id, comment_in=comment_in)


@router.get("/ads/{ad_id}/comments/", response_model=list[CommentOut])
def list_comments_for_ad(
    ad_id: int,
    db: Session = Depends(get_db),
):
    service = CommentService(db)
    return service.get_comments_by_ad(ad_id=ad_id)
