from fastapi import APIRouter, Depends, status

router = APIRouter(
    prefix='/api/v1',
    tags=['Authentication']
)


@router.get("/kamron")
async def say_hello():
    print("goodo")
    return "Kamron"
