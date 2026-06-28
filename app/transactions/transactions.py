from fastapi import APIRouter, status, Request, HTTPException, Depends
from app.auth.jwt_handler import get_current_user
from app.core.database import create_database_connection
from .schemas import Transfer

transfer = APIRouter(prefix="/transfer", tags=["transfer"])


@transfer.post("/")
def send(payload: Transfer, current_user: dict = Depends(get_current_user)):

    conn, cursor = create_database_connection()

    try:
        cursor.execute(
            """select * from user_balance 
                    where user_id = %s""",
            (payload.to,),
        )
        user = cursor.fetchone()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with {id} dors not exist!",
            )

        cursor.execute(
            """select * from user_balance 
                    where user_id = %s""",
            (current_user["user_id"],),
        )
        user = cursor.fetchone()
        if user["balance"] < payload.amount:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail=f"Your account balance is less than {payload.amount}",
            )

        cursor.execute(
            """update user_balance
                    set balance = balance - %s
                    where user_id = %s """,
            (payload.amount, current_user["user_id"]),
        )
        cursor.execute(
            """
                        update user_balance
                    set balance = balance + %s
                    where user_id = %s""",
            (
                payload.amount,
                payload.to,
            ),
        )

        cursor.execute(
            """insert into transactions (user_id,transaction_type,amount)
                    values (%s,%s,%s)""",
            (
                current_user["user_id"],
                "transfer",
                payload.amount,
            ),
        )
        conn.commit()
        return {"message": "transaction Successful"}

    finally:
        conn.close()
        cursor.close()
