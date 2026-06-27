from fastapi import APIRouter , status , Request , HTTPException 



transactions = APIRouter(
    prefix = "/transactions",
    tags = ["transaction"]
)

@transactions.get("/current_balance")
def current_balance(payload : )