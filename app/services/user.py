from datetime import datetime
import os
import random
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.config import APP_DIR, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from app.models.land import LandInfo, LandListing
from app.models.user import User, UserFavoriteLand
from app.services.land import land_service

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def reset_password(self, email: str, db: Session) -> str:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("이메일이 존재하지 않습니다.")

        random_password = (
            "".join(random.sample(string.ascii_letters, 8))
            + "".join(random.sample(string.digits, 3))
            + "".join(random.sample(string.punctuation, 1))
        )

        user.password = password_context.hash(random_password)
        db.commit()
        
        self._send_email(email, random_password)
        return random_password

    def _send_email(self, email: str, new_password: str):
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = email
        msg["Subject"] = "비밀번호 초기화"
        body = f"""새로운 비밀번호는 아래와 같습니다.

PW: {new_password}

계정에 접속하여 비밀번호를 변경하실 것을 권장드립니다.
감사합니다.
"""
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, email, msg.as_string())
        server.quit()

    def get_user_image(self, file_name: Optional[str] = None) -> FileResponse:
        if not file_name:
            return FileResponse(os.path.join(APP_DIR, "static/images/default-user-image.png"))
        return FileResponse(os.path.join(APP_DIR, "static/images/", file_name))

    def modify_user_info(
        self,
        name: str,
        nickname: str,
        phone: str,
        is_image_deleted: bool,
        image: Optional[UploadFile],
        payload: dict,
        db: Session,
    ):
        if not payload:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
        email = payload.get("sub")
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")
        if is_image_deleted:
            user.profile_image_url = None
        elif image:
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            file_extension = os.path.splitext(image.filename)[1]
            saved_file_name = f"{current_time}_{secrets.token_hex(16)}{file_extension}"
            file_path = os.path.join(APP_DIR, "static/images/", saved_file_name)
            with open(file_path, "wb+") as b:
                b.write(image.file.read())
            user.profile_image_url = "/user/images/" + saved_file_name

        user.name = name
        user.nickname = nickname
        user.phone = phone
        db.commit()

    def change_password(self, current_password: str, new_password: str, payload: dict, db: Session):
        if not payload:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
        email = payload.get("sub")
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")
        if not password_context.verify(current_password, user.password):
            raise HTTPException(status_code=400, detail="현재 비밀번호가 일치하지 않습니다.")
        user.password = password_context.hash(new_password)
        db.commit()

    def toggle_favorite(self, pnu: str, payload: dict, db: Session) -> bool:
        if not payload:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
        email = payload.get("sub")
        user = db.query(User).filter_by(email=email).first()
        land = db.query(LandInfo).filter_by(pnu=pnu).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")
        if not land:
            raise HTTPException(status_code=404, detail="토지 데이터가 존재하지 않습니다.")
        favorite_land = (
            db.query(UserFavoriteLand)
            .filter(
                UserFavoriteLand.user_id == user.user_id,
                UserFavoriteLand.pnu == pnu,
            )
            .first()
        )
        if favorite_land:
            land.like_count = max(land.like_count - 1, 0)
            db.delete(favorite_land)
        else:
            land.like_count += 1
            new_favorite = UserFavoriteLand(user_id=user.user_id, pnu=pnu)
            db.add(new_favorite)
        db.add(land)
        db.commit()
        return favorite_land is None

    def get_favorite_lands(self, payload: dict, db: Session):
        if not payload:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
        email = payload.get("sub")
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")
        favorites = (
            db.query(UserFavoriteLand)
            .filter(UserFavoriteLand.user_id == user.user_id)
            .all()
        )
        fav_data = []
        for fav in favorites:
            land, _ = land_service.get_land_detail(pnu=fav.pnu, payload=None, db=db)
            fav_data.append(land)
        return fav_data
    
    def get_listings(self, payload: dict, db: Session):
        if not payload:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
        email = payload.get("sub")
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")
        listings = (
            db.query(LandListing)
            .filter(LandListing.user_id == user.user_id)
            .all()
        )
        listings_data = []
        for listing in listings:
            land, _ = land_service.get_land_detail(pnu=listing.pnu, payload=None, db=db)
            listings_data.append(land)
        return listings_data


user_service = UserService()
