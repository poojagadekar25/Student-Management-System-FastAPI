from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=50), unique=True, index=True)
    password = Column(String(length=255))
    email = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(String(length=50))  # "student" or "teacher"
    
    

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    name = Column(String(length=50))
    marks = Column(Integer)
    role=Column(String(length=50))
    attendance = Column(Integer, default=0)  # If you want numeric default values


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True,index=True)
    name = Column(String(length=50))
    description = Column(String(length=50))




# class Enrollment(Base):
#     __tablename__ = "enrollments"
#     student_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
#     course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)






