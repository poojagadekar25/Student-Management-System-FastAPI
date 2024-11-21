from sqlalchemy.orm import Session
import models, schemas,auth_utils
from fastapi import HTTPException

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    # Check for existing user with the same username or email
    existing_user = db.query(models.User).filter(
        (models.User.username == user.username) | 
        (models.User.email == user.email)).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    # Hash the password
    hashed_password = auth_utils.get_password_hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password, email=user.email, role=user.role)
    try:
        # Add and commit the user to the database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # If the user is a student, create a StudentProfile entry
        if db_user.role == "student":
            student_profile = models.StudentProfile(
                id=db_user.id,  # Foreign key linking to `users.id`
                name=user.username,  # Or another field for the name
                marks=0, 
                attendance=0, # Default marks
                role="student",
            )
            db.add(student_profile)
            db.commit()  # Commit the student profile creation

    except Exception as e:
        db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=400, detail="Error creating user: " + str(e))
    
    return db_user

def get_courses(db: Session):
    return db.query(models.Course).all()

def get_student_profile(db: Session, student_id: int):
    return db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()


def update_marks(db: Session, student_id: int, marks: int):
    student_profile = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if student_profile is None:
        raise HTTPException(status_code=404, detail="Student not found")

    student_profile.marks = marks
    db.commit()
    db.refresh(student_profile)
    return student_profile

def get_course_by_name(db:Session,name:str):
    return db.query(models.Course).filter(models.Course.name == name).first()

def add_course(db: Session, id: int, name: str, description: str):
    # Check if the course already exists
    course = db.query(models.Course).filter(models.Course.id == id).first()
    if course:
        raise HTTPException(status_code=400, detail="Course with this ID already exists")
    
    # Create a new course instance
    new_course = models.Course(id=id, name=name, description=description)
    db.add(new_course)  
    db.commit()  
    db.refresh(new_course)  
    return new_course  

def update_attendence(db: Session, student_id: int, attendance: int):
    student_profile = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if student_profile is None:
        raise HTTPException(status_code=404, detail="Student not found")
    student_profile.attendance = attendance
    db.commit()
    db.refresh(student_profile)
    return student_profile

    

