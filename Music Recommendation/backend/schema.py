from pydantic import BaseModel

class RequestToken(BaseModel):
    uuid: str

