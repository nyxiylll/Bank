from pydantic import BaseModel 

class Transfer(BaseModel):
    amount : int 
    to : str