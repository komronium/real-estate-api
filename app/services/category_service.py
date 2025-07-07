from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category, CategoryName
from app.models.user import User, UserRole
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    @staticmethod
    def verify_admin(current_user: User):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can perform this action"
            )
        return current_user

    @staticmethod
    def create_category(category_data: CategoryCreate, current_user: User, db: Session):
        CategoryService.verify_admin(current_user)

        if category_data.parent_id:
            parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")

        new_category = Category(parent_id=category_data.parent_id)
        db.add(new_category)
        db.commit()

        for lang, name in category_data.names.items():
            category_name = CategoryName(
                category_id=new_category.id,
                lang=lang,
                name=name
            )
            db.add(category_name)

        db.commit()
        db.refresh(new_category)
        return new_category

    @staticmethod
    def get_all_categories(db: Session):
        categories = db.query(Category).all()
        result = []
        for category in categories:
            names = {t.lang: t.name for t in category.names}
            result.append({
                "id": category.id,
                "names": names,
                "parent_id": category.parent_id,
            })
        return result

    @staticmethod
    def get_root_categories(db: Session):
        return db.query(Category).filter(Category.parent_id == None).all()

    @staticmethod
    def get_category_by_id(category_id: int, db: Session):
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    @staticmethod
    def update_category(category_id: int, category_data: CategoryUpdate, current_user: User, db: Session):
        CategoryService.verify_admin(current_user)

        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if category_data.parent_id:
            parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")

            if parent.id == category_id:
                raise HTTPException(status_code=400, detail="A category cannot be its own parent")

        for key, value in category_data.model_dump().items():
            if value is not None:
                setattr(category, key, value)

        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(category_id: int, current_user: User, db: Session):
        # Verify admin privileges
        CategoryService.verify_admin(current_user)

        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if category.subcategories:
            raise HTTPException(status_code=400, detail="Cannot delete category with subcategories")

        if category.ads:
            raise HTTPException(status_code=400, detail="Cannot delete category with associated ads")

        db.delete(category)
        db.commit()