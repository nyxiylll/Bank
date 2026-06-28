from fastapi import FastAPI , Request , status , HTTPException
from app.users.schemas import UserRegister , UserDelete
from app.core.database import create_database_connection 
from app.core.security import create_hash , verify_hash
from app.users.routes import user
from app.accounts.routes import bank
from app.transactions.transactions import transfer

app = FastAPI(title = "Banking Service")
app.include_router(user)
app.include_router(bank)
app.include_router(transfer)

@app.get("/")
async def root():
    return {"Message":"Welcome to Banking Service"}


