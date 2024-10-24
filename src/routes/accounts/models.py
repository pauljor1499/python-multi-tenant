from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Union
from datetime import datetime, timezone
from bson import ObjectId


class SchoolAdminAccount(BaseModel):
    email: str
    password: str
    role: str = "admin"
    school_code: Optional[str] = None

class SchoolTeacherAccount(BaseModel):
    email: str
    password: str
    role: str = "teacher"
    school_code: Optional[str] = None

class SchoolStudentAccount(BaseModel):
    email: str
    password: str
    role: str = "student"
    school_code: Optional[str] = None

class SchoolAccount(BaseModel):
    name: str
    school_code: str