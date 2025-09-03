"""
Database initialization script
Creates tables and adds initial data
"""
import logging
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.models.user import User, UserRole
from app.core.security import hash_password

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize database with tables and initial data"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Add initial data if needed
        # create_initial_data()
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def create_initial_data() -> None:
    """Create initial data like admin user"""
    from app.db.session import SessionLocal
    
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin_user:
            # Create default admin user
            admin_user = User(
                username="admin",
                password=hash_password("admin123"),  # Change this in production
                role=UserRole.ADMIN,
                name="System Administrator"
            )
            db.add(admin_user)
            db.commit()
            logger.info("Default admin user created")
        else:
            logger.info("Admin user already exists")
            
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
