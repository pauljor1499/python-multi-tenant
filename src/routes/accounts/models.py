from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Union
from datetime import datetime, timezone
from bson import ObjectId


class SchoolAdminAccount(BaseModel):
    email: str
    password: str
    school_code: Optional[str] = None

class SchoolAccount(BaseModel):
    name: str
    school_code: str