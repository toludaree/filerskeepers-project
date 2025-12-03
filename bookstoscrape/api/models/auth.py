from pydantic import BaseModel, EmailStr


class UserData(BaseModel):
    email: EmailStr
    password: str

class SignUp(BaseModel):
    message: str

class Login(BaseModel):
    access_token: str

class GenerateApiKey(BaseModel):
    key: str
