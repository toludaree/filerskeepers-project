from pydantic import BaseModel, EmailStr


class UserData(BaseModel):
    email: EmailStr
    password: str

class SignUpResponseSchema(BaseModel):
    message: str

class LoginResponseSchema(BaseModel):
    access_token: str

class GenerateApiKeyResponseSchema(BaseModel):
    key: str
