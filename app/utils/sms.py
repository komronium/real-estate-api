from eskiz.client import AsyncClient

from app.core.config import settings


async def create_client():
    return AsyncClient(
        email=settings.ESKIZ_EMAIL,
        password=settings.ESKIZ_PASSWORD.get_secret_value(),
    )
        

async def send_sms(phone_number: str, code: str):
    client = await create_client()
    async with client:
        response = await client.send_sms(
            phone_number=phone_number,
            message=f"QAVAT.UZ saytiga kirish uchun tasdiqlash kodi: {code}",
        )
        return response
