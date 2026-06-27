from fastapi import APIRouter, HTTPException , status , Depends
from app.auth.jwt_create import get_current_user
from app.database import create_database_connection

bank = APIRouter(
    prefix = "/bank",
    tags = ["Bank"]
)

@bank.post("/deposit")
def deposit(amount : int ,current_user : dict = Depends(get_current_user)):

    if amount < 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Minimum amount is 500")
    conn , cursor = create_database_connection()
    try:
        cursor.execute('''select from user_balance 
                        where user_id = %s''',
                        (current_user["id"],))
        user = cursor.fetchone()
        if user is None:
            cursor.execute('''insert into user_balance (user_id , balance,status),
                            values (%s,%s,%s)''',
                            (current_user["id"],amount,"is_active"))
