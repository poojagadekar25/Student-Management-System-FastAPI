from fastapi import FastAPI, Depends, HTTPException, status,Request
from sqlalchemy.orm import Session
import models
import schemas
import auth_utils
import crud
from database import SessionLocal, engine,get_db
from jose import JWTError, jwt
from auth_utils import get_current_user,get_teacher_user
from models import User
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from datetime import datetime, timedelta

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Predefined code for teacher registration (this would be securely stored in production)
TEACHER_AUTH_CODE = "9767432450" 
# # Dependency for DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

#No authentication Required
@app.get("/start")
def welcome():
    return {"Messege":"Welcome To Pravara Rural Engineering College"}

# Student Registration Endpoint
@app.post("/register", response_model=schemas.UserResponse)
def register_student(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username is already taken
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.role != "student":
        raise HTTPException(status_code=400, detail="Invalid role. Only 'Student' role is allowed.")
    # Register the user
    return crud.create_user(db, user)


# Teacher Regisctration Endpoint with Code Verification
@app.post("/register_teacher", response_model=schemas.UserResponse)
def register_teacher(user: schemas.UserCreateTeacher, db: Session = Depends(get_db)):
    # Check authorization code for teacher registration
    if user.auth_code != TEACHER_AUTH_CODE:
        raise HTTPException(status_code=403, detail="Invalid authorization code")   
    # Check if username is already taken
    db_user = crud.get_user_by_username(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.role != "Teacher":
        raise HTTPException(status_code=400, detail="Invalid role. Only 'Teacher' role is allowed.")
    # Register the user as teacher
    return crud.create_user(db, user)


@app.post("/token")
async def login_for_access_token(db: Session = Depends(get_db),form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/course/", response_model=schemas.Course)
def add_courses(course: schemas.Course, db: Session = Depends(get_db), current_user = Depends(auth_utils.get_teacher_user)):
    # Check if the current user is a teacher
    if current_user.role != "Teacher":
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Check if the course already exists by name
    existing_course = crud.get_course_by_name(db, course.name)
    if existing_course:
        raise HTTPException(status_code=400, detail="Course with this name already registered")
    
    # Call the function to add the course
    return crud.add_course(db, id=course.id, name=course.name, description=course.description)

@app.get("/courses", response_model=list[schemas.Course])
def read_courses(db: Session = Depends(get_db)):
    return crud.get_courses(db)



@app.put("/teacher/update-marks")
def update_student_marks(student_id: int, marks: int, db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_teacher_user)):
    # Check the current user's role
    if current_user.role != "Teacher":
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Update marks for the specified student
    return crud.update_marks(db, student_id, marks)

@app.put("/attendence/")
def add_attendence(student_id: int, attendence: int, db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_teacher_user)):
    # Check the current user's role
    if current_user.role != "Teacher":
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Update marks for the specified student
    return crud.update_attendence(db, student_id, attendence)



@app.get("/student/profile", response_model=schemas.StudentProfile)  # Create a new response model that includes marks
def read_student_profile(db: Session = Depends(get_db), current_user: User = Depends(auth_utils.get_current_user)):
    # Check if current user has a student role
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Access forbidden")
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    profile = db.query(models.StudentProfile).filter(models.StudentProfile.id == current_user.id).first()
    # Retrieve profile and return
    #profile = crud.get_student_profile(db, current_user.id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    #return profile
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "name": profile.name,
        "marks": profile.marks,
        "attendance":profile.attendance
    }


@app.delete("/students/{student_id}", response_model=dict)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if the user has a "teacher" role
    print("Current user role in delete endpoint:", current_user.role)
    if current_user.role != "Teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can perform this action"
        )
    
    student_profile = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if student_profile:
        db.delete(student_profile)
        db.commit()  # Commit to remove the profile first

    # Now delete the user
    user = db.query(models.User).filter(models.User.id == student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(user)
    db.commit()  # Commit the user deletion
    return {"message": "Student deleted successfully"}

   




