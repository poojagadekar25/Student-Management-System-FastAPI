from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from database import get_db
from fastapi import Depends, HTTPException,status,Header
from sqlalchemy.orm import Session
from jose import JWTError, jwt  
from models import User  
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = "5947ac268a7ea2cb5a9e3b19f0825335949dd3bc7e7dd9db3499fdc3a273797f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#Thisexpects clients to send an access token in the Authorization header of the HTTP request.


class TokenData(BaseModel):
    username: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    # Query your database here instead of the in-memory `db` example.
    user_data = db.query(User).filter(User.username == username).first()
    if user_data:
        return user_data
    return None

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credential_exception
    return user

def get_teacher_user(current_user: User = Depends(get_current_user)) -> User:
    # Debugging statement to check current_user attributes
    print("Current user:", current_user.username)
    print("Current user role:", current_user.role)  # Check if the role is retrieved

    if current_user.role != "Teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can perform this action"
        )
    return current_user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

