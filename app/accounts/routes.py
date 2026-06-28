from fastapi import APIRouter, HTTPException, status, Depends
from app.auth.jwt_handler import get_current_user
from app.core.database import create_database_connection
from .schemas import Post

bank = APIRouter(prefix="/bank", tags=["Bank"])


@bank.get("/check_balance")
def check(current_user: dict = Depends(get_current_user)):

    conn, cursor = create_database_connection()
    try:
        cursor.execute(
            """select balance from user_balance
                    where user_id = %s""",
            (current_user["user_id"],),
        )
        balance = cursor.fetchone()
        return {"message": balance}
    finally:
        conn.close()
        cursor.close()


@bank.post("/deposit")
def deposit(payload : Post, current_user: dict = Depends(get_current_user)):

    if payload.amount < 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Minimum amount is 500"
        )
    conn, cursor = create_database_connection()
    try:
        cursor.execute(
            """update user_balance
                    set balance = balance + %s
                    where user_id = %s""",
            (payload.amount, current_user["user_id"]),
        )

        user_id = current_user["user_id"]
        transaction_type = "Deposit"
        amount = payload.amount
        cursor.execute(
            """
                    insert into transactions (user_id,transaction_type,amount)
                        values (%s,%s,%s)""",
            (user_id, transaction_type, amount),
        )
        conn.commit()
        return {"message": f"amount {amount}added successfully"}
    finally:
        conn.close()
        cursor.close()


@bank.post("/withdraw")
def withdraw(payload : Post, current_user: dict = Depends(get_current_user)):

    conn, cursor = create_database_connection()

    try:
        cursor.execute(
            """
            select * from user_balance 
            where user_id = %s""",
            (current_user["user_id"],),
        )
        user = cursor.fetchone()
        if user["balance"] < payload.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="your account does not have that balance",
            )
        cursor.execute(
            """update user_balance
                    set balance = balance - %s
                    where user_id = %s""",
            (payload.amount, current_user["user_id"]),
        )
        user_id = current_user["user_id"]
        transaction_type = "Withdrawl"
        amount = payload.amount
        cursor.execute(
            """
                    insert into transactions (user_id,transaction_type,amount)
                        values (%s,%s,%s)""",
            (user_id, transaction_type, amount),
        )
        conn.commit()
        return {"message": "Amount withdraw was successful"}
    finally:
        conn.close()
        cursor.close()
