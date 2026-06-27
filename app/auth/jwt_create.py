from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.database import create_database_connection
from dotenv import load_dotenv
import jwt
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/user/login")


def create_token(payload: dict) -> str:
    token_data = payload.copy()
    token_data.update(
        {
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
    )
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token: str) -> dict | None:
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_payload
    except jwt.PyJWTError:  
        return None


def get_current_user(token: str = Depends(oauth2_bearer)) -> dict:
    conn, cursor = create_database_connection()
    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        payload = decode_token(token)
        if not payload:
            raise credentials_exception

        user_id = str(payload.get("id"))
        user_email = str(payload.get("email"))
        if not user_id and not user_email:
            raise credentials_exception

        cursor.execute('''Select * from users 
                        where user_id = %s or email = %s''',
                        (user_id,user_email,))
        user = cursor.fetchone()
        if user is None:
            raise credentials_exception
        return user
    finally:
        conn.close()
        cursor.close()
