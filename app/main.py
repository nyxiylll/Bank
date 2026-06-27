from fastapi import FastAPI , Request , status , HTTPException
from app.models import UserRegister , UserDelete
from app.database import create_database_connection 
from app.utils import create_hash , verify_hash
from app.routes.user import user
from app.routes.bank import bank

app = FastAPI(title = "Banking Service")
app.include_router(user)
app.include_router(bank)

@app.get("/")
async def root():
    return {"Message":"Welcome to Banking Service"}


