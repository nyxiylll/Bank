from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.users.schemas import UserRegister
from app.core.database import create_database_connection
from app.core.security import create_hash, verify_hash
from app.auth.jwt_handler import create_token, get_current_user

user = APIRouter(prefix="/user", tags=["User"])


@user.post("/register")
def register(payload: UserRegister):
    conn, cursor = create_database_connection()
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s;", (payload.email,))
        existing_user = cursor.fetchone()
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists with this email",
            )

        cursor.execute(
            """INSERT INTO users (first_name, last_name, email, password)
            VALUES (%s, %s, %s, %s);""",
            (
                payload.first_name,
                payload.last_name,
                payload.email,
                create_hash(payload.password),
            ),
        )

        conn.commit()
        return {"Message": "Account created"}
    finally:
        cursor.close()
        conn.close()


@user.post("/login")
def login(formdata: OAuth2PasswordRequestForm = Depends()):
    conn, cursor = create_database_connection()
    try:
        email = formdata.username
        password = formdata.password

        cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
        db_user = cursor.fetchone()

        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Go ahead and register first!",
            )

        is_password = verify_hash(password, db_user["password"])
        if not is_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password Invalid",
            )

        cursor.execute(
            """
            select user_id from user_balance where user_id = %s""",
            (db_user["user_id"],),
        )
        is_user = cursor.fetchone()
        if is_user is None:
            initial_balance = 0
            account_status = "is_active"
            cursor.execute(
                """Insert into user_balance (user_id,balance,status)
                values (%s,%s,%s);""",
                (db_user["user_id"], initial_balance, account_status),
            )
            conn.commit()

        token_payload = {
            "id": db_user["user_id"],
            "email": db_user["email"],
        }

        access_token = create_token(token_payload)
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        cursor.close()
        conn.close()


@user.delete("/delete")
def delete(current_user: dict = Depends(get_current_user)):
    conn, cursor = create_database_connection()
    try:
        user_email = current_user["email"]

        cursor.execute("DELETE FROM users WHERE email = %s;", (user_email,))
        conn.commit()
        return {"Message": "Account Deleted Successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account due to a database error.",
        )
    finally:
        cursor.close()
        conn.close()


@user.get("/")
def current_user(payload: dict = Depends(get_current_user)):
    return {"message": payload}
