from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Union
from datetime import datetime, timezone
from bson import ObjectId


class ObjectIdField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field):
        if isinstance(v, ObjectId):
            return v  # Return ObjectId directly
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)  # Convert string to ObjectId
        raise TypeError('ObjectId required')

    @classmethod
    def __get_pydantic_json_schema__(cls, *args, **kwargs):
        return {"type": "string"}

class SchoolAdminAccount(BaseModel):
    email: str
    password: str
    role: str = "admin"
    school: ObjectIdField

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