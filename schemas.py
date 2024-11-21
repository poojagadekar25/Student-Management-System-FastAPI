from pydantic import BaseModel,EmailStr,Field

class UserCreateTeacher(BaseModel):
    username: str= Field(..., min_length=1, max_length=50, pattern=r"^[A-Za-z\s]+$")
    password: str
    email:EmailStr
    role: str = "Teacher"
    auth_code: str

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, pattern=r"^[A-Za-z\s]+$")
    password: str
    email:EmailStr
    role: str = "student"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email:str
    username: str
    role: str
    class Config:
         from_attributes = True

class StudentProfile(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    marks: int
    attendance:int=0

    class Config:
        from_attributes = True 

class Course(BaseModel):
    id: int 
    name: str
    description: str

class Token(BaseModel):
    access_token: str
    token_type: str

