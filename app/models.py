from pydantic import BaseModel , EmailStr , Field
from uuid import UUID , uuid4

class UserRegister(BaseModel):
    id : None
    first_name : str
    last_name : str
    email : EmailStr
    password : str

class UserDelete(BaseModel):
    email : EmailStr
    password : str

class UserLogin(BaseModel):
    email : EmailStr
    password : str
