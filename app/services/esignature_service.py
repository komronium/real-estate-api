import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.user import User
from app.schemas.eimzo import Base64Dto


class ESignatureService:

    def __init__(self, db: Session):
        self.db = db

    async def authenticate(self, dto: Base64Dto):
        json_response = self.request_eimzo(dto.data)

        status = json_response.get("status")

        if status == 1:
            cert = json_response.get("cert", {})
            subject = cert.get("subjectNameFieldMap", {})
            serial_number = cert.get("serialNumber")

            if not serial_number:
                raise HTTPException(status_code=400, detail="Sertifikatda serial raqam yo'q")

            existing_user = ESignatureService().get_user_by_serial(serial_number, db)
            if existing_user:
                return create_access_token({"sub": existing_user.id})

            subject_data = ESignatureService().parse_subject_fields(subject)
            new_user = {
                "username": subject_data["inn"],
                "inn": subject_data["inn"],
                "full_name": subject_data["full_name"],
                "organization": subject_data["organization"],
                "organization_address": f'{subject_data["region"]} {subject_data["city"]}',
                "email": subject_data["email"],
                "serial_number": serial_number,
                # "password": pwd_context.hash(subject_data["inn"]),
                "eimzo": True,
            }
            user_db = ESignatureService().save_user(new_user, self.db)
            return create_access_token({"sub": user_db.id})
        elif status == -1:
            raise HTTPException(status_code=400, detail="Sertifikat statusini tekshirib bo‘lmadi")
        elif status == -5:
            raise HTTPException(status_code=400, detail="Imzo vaqti xato. Kompyuter vaqti noto‘g‘ri.")
        elif status == -10:
            raise HTTPException(status_code=400, detail="ERI yaroqsiz")
        elif status == -11:
            raise HTTPException(status_code=400, detail="Sertifikat yaroqsiz")
        elif status == -12:
            raise HTTPException(status_code=400, detail="Sertifikat sanada haqiqiy emas")
        elif status == -20:
            raise HTTPException(status_code=400, detail="Challenge topilmadi yoki muddati o‘tgan")
        else:
            raise HTTPException(status_code=400, detail="Noma’lum xatolik")

    @staticmethod
    def request_eimzo(data: str):
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

    def save_user(self, user_data):
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    @staticmethod
    def parse_subject_fields(subject: dict):
        return {
            "inn": subject.get("1.2.860.3.16.1.1"),
            "full_name": subject.get("CN"),
            "organization": subject.get("O"),
            "region": subject.get("ST"),
            "city": subject.get("L"),
            "email": subject.get("E")
        }
