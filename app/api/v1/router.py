from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, profile, otp, ad, ad_image, category, comment, popular_ads, one_id, verification, admin_verification, statistics

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(one_id.router)  # One ID auth endpoint
api_router.include_router(otp.router)
api_router.include_router(users.router)
api_router.include_router(profile.router)
api_router.include_router(ad.router)
api_router.include_router(ad_image.router)
api_router.include_router(category.router)
api_router.include_router(comment.router)
api_router.include_router(popular_ads.router)
api_router.include_router(verification.router)
api_router.include_router(admin_verification.router)
api_router.include_router(statistics.router)
