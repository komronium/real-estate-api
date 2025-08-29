from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from app.models.category import Category, CategoryName
from app.models.user import User, UserRole
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.utils.s3_upload import s3_service


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
    async def upload_category_icon(category_id: int, icon_file: UploadFile, current_user: User, db: Session):
        """
        Upload icon for a specific category
        """
        CategoryService.verify_admin(current_user)
        
        # Verify category exists
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Validate file
        if not s3_service.is_valid_image(icon_file):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only images (JPEG, PNG, GIF, WebP) are allowed"
            )
        
        # Check file size (max 5MB)
        if s3_service.get_file_size_mb(icon_file) > 5:
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum size is 5MB"
            )
        
        try:
            # Delete old icon if exists
            if category.icon:
                await s3_service.delete_file(category.icon)
            
            # Upload new icon
            icon_url = await s3_service.upload_file(icon_file, folder="category_icons")
            
            # Update category with new icon URL
            category.icon = icon_url
            db.commit()
            db.refresh(category)
            
            return category
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload icon: {str(e)}"
            )

    @staticmethod
    async def delete_category_icon(category_id: int, current_user: User, db: Session):
        """
        Delete icon for a specific category
        """
        CategoryService.verify_admin(current_user)
        
        # Verify category exists
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        if not category.icon:
            raise HTTPException(status_code=400, detail="Category has no icon to delete")
        
        try:
            # Delete from S3
            await s3_service.delete_file(category.icon)
            
            # Remove icon URL from category
            category.icon = None
            db.commit()
            db.refresh(category)
            
            return {"message": "Icon deleted successfully"}
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete icon: {str(e)}"
            )

    @staticmethod
    def create_category(category_data: CategoryCreate, current_user: User, db: Session):
        CategoryService.verify_admin(current_user)

        if category_data.parent_id:
            parent = db.query(Category).filter(Category.id == category_data.parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")

        new_category = Category(
            parent_id=category_data.parent_id,
            icon=category_data.icon
        )
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
        return db.query(Category).all()

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