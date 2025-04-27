import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.user import User
from app.schemas.eimzo import Base64Dto
from app.services.auth_service import AuthService


class ESignatureService:

    def __init__(self, db: Session):
        self.db = db

    async def authenticate(self, dto: Base64Dto):
        response = self.request_eimzo(dto.data)
        status = response.get("status")

        if status != 1:
            raise HTTPException(status_code=400, detail="E-IMZO authentication failed")

        cert = response.get("cert", {})
        subject = cert.get("subjectNameFieldMap", {})
        serial_number = cert.get("serialNumber")

        if not serial_number:
            raise HTTPException(status_code=400, detail="No serial number in certificate")

        user = self.get_user_by_serial(serial_number)
        if not user:
            subject_data = self.parse_subject_fields(subject)
            user = self.save_user(subject_data, serial_number)

        auth_service = AuthService(self.db)
        return auth_service.create_token(user)

    def request_eimzo(self, data: str):
        url = "http://127.0.0.1:8080/backend/auth"
        headers = {
            "X-Real-IP": "195.158.18.45",
            "Host": "isbn.natlib.uz",
            "Content-Type": "text/plain"
        }

        try:
            response = requests.post(url, data=data.encode("utf-8"), headers=headers)
            response.raise_for_status()
            json_start = response.text.find("{")
            return response.json() if json_start == -1 else response.json()
        except Exception as e:
            print("Xatolik:", str(e))
            raise HTTPException(status_code=400, detail="E-Imzo bilan ulanishda xatolik")

    def get_user_by_serial(self, serial_number: str):
        return self.db.query(User).filter(User.serial_number == serial_number).first()

    def save_user(self, data: dict, serial_number: str):
        user = User(**data, serial_number=serial_number)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def parse_subject_fields(self, fields: dict) -> dict:
        return {
            "inn": fields.get("1.2.860.3.16.1.1"),
            "full_name": fields.get("CN"),
            "organization": fields.get("O"),
            "region": fields.get("ST"),
            "city": fields.get("L")
        }
