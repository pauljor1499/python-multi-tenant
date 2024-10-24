from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Union
from datetime import datetime, timezone
# from beanie import Document
from bson import ObjectId
from src.routes.question_bank.validations.input_validations import QuestionType, AssignmentType, Category, DifficultyType
from src.routes.question_bank.validations.field_validations import (
    validate_question_field,
    validate_choices_field,
    validate_correct_answer_field,
    validate_question_details_field,
    validate_assignment_type_field,
    validate_question_type_field,
    validate_difficulty_field,
    validate_teks_code_field,
    validate_points_field,
    validate_category_field,
    validate_deleted_field,
    validate_deleted_date_field,
    validate_created_date_field,
    validate_updated_date_field
)

class ObjectIdField(str):
    """Custom ObjectId type for Pydantic."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)  # Return ObjectId as string
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)  # Convert string to ObjectId
        raise TypeError('ObjectId required')

    @classmethod
    def __get_pydantic_json_schema__(cls, *args, **kwargs):
        return {"type": "string"}


class Item(BaseModel):
    id: int
    text: str = Field(..., max_length=300)

class Select(BaseModel):
    id: int
    items: List[Item]

class Answer(BaseModel):
    id: int
    answer: str = Field(..., max_length=300)

class CorrectAnswer(BaseModel):
    answers: Union[List[Answer], List[str], str]
    answerDetails: str = Field(None, max_length=300)

class QuestionModelCreate(BaseModel):
    questionType: QuestionType
    question: str = Field(..., max_length=300)
    choices: Optional[List[Union[Item, Select]]] = None
    correctAnswer: CorrectAnswer
    questionDetails: Optional[str] = Field(None, max_length=300)
    assignmentType: AssignmentType
    difficulty: DifficultyType
    teksCode: Optional[str] = Field(None)
    points: str = Field(..., max_length=3)
    category: Optional[Category] = None
    createdDate:  datetime = datetime.now(timezone.utc)
    # createdBy: Optional [ObjectIdField] = None
    deleted: Optional[bool] = False
    deletedDate: Optional[datetime] = None
    # deletedBy: Optional[ObjectIdField] = None
    updatedDate: Optional[datetime] = None
    # updatedBy: Optional[ObjectIdField] = None
    
    @model_validator(mode='before')
    def validate_fields(cls, values):
        validate_question_field(values)
        validate_choices_field(values)
        validate_correct_answer_field(values)
        validate_question_details_field(values)
        validate_assignment_type_field(values)
        validate_question_type_field(values)
        validate_difficulty_field(values)
        validate_teks_code_field(values)
        validate_points_field(values)
        validate_category_field(values)
        validate_deleted_field(values)
        validate_deleted_date_field(values)
        validate_created_date_field(values)
        validate_updated_date_field(values)
        return values
    
    class Config:
        arbitrary_types_allowed = True


class QuestionModelUpdate(BaseModel):
    questionType: Optional[QuestionType] = None
    question: Optional[str] = Field(None, max_length=300)
    choices: Optional[List[Union[Item, Select]]] = None
    correctAnswer: Optional[CorrectAnswer] = None
    questionDetails: Optional[str] = Field(None, max_length=300)
    assignmentType: Optional[AssignmentType] = None
    difficulty: Optional[DifficultyType] = None
    teksCode: Optional[str] = Field(None)
    points: Optional[str] = Field(None, max_length=3)
    category: Optional[Category] = None
    updatedDate: datetime = datetime.now(timezone.utc)
    updatedBy: Optional[ObjectIdField] = None
    
    @model_validator(mode='before')
    def validate_fields(cls, values):
        validate_question_field(values)
        validate_choices_field(values)
        validate_correct_answer_field(values)
        validate_question_details_field(values)
        validate_assignment_type_field(values)
        validate_question_type_field(values)
        validate_difficulty_field(values)
        validate_teks_code_field(values)
        validate_points_field(values)
        validate_category_field(values)
        validate_deleted_field(values)
        validate_deleted_date_field(values)
        validate_created_date_field(values)
        validate_updated_date_field(values)
        return values
    
    class Config:
        arbitrary_types_allowed = True