from pydantic import BaseModel

class UserRequestCO(BaseModel):
    name: str
    email: str
    password: str
    role: str

class UserResponseDTO(BaseModel):
    name: str
    email: str
    class Config:
        from_attributes = True

class UserLoginRequestCO(BaseModel):
    email: str
    password: str