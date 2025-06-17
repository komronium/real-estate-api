from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, profile, otp, ad, ad_image, category, comment

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(otp.router)
api_router.include_router(users.router)
api_router.include_router(profile.router)
api_router.include_router(ad.router)
api_router.include_router(ad_image.router)
api_router.include_router(category.router)
api_router.include_router(comment.router)
