from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.schemas.comment import CommentCreate

class CommentService:

    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, ad_id: int, user_id, comment_in: CommentCreate):
        comment = Comment(ad_id=ad_id, user_id=user_id, text=comment_in.text)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_comments_by_ad(self, ad_id: int):
        return self.db.query(Comment).filter(Comment.ad_id == ad_id).order_by(Comment.created_at.desc()).all()
