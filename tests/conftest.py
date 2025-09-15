import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    from app.models.user import User, UserRole
    from app.core.security import hash_password
    
    user = User(
        username="admin",
        password=hash_password("admin123"),
        role=UserRole.ADMIN,
        phone_number="+998901234567"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_ad(db, admin_user):
    from app.models.ad import Ad, DealType
    from app.models.category import Category
    
    # Create category first
    category = Category(name="Apartment", description="Residential apartments")
    db.add(category)
    db.commit()
    db.refresh(category)
    
    ad = Ad(
        title="Test Apartment",
        description="Test description",
        price=100000,
        deal_type=DealType.sale,
        category_id=category.id,
        user_id=admin_user.id,
        latitude=41.33575242335,
        longitude=69.21214325235,
        full_name="Test User",
        email="test@example.com",
        phone_number="+998901234567"
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad

