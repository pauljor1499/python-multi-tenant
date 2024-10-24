from fastapi import Request, APIRouter, Body
from src.routes.question_bank.service import QuestionService
from src.routes.question_bank.models import QuestionUpdate
from src.routes.question_bank.utilities.payloads import questions


router = APIRouter()

question_service = QuestionService()

@router.get("", response_model=dict)
async def fetch_questions(query: Request) -> dict:
    query_dict = dict(query.query_params)
    return await question_service.fetch_questions(query_dict)

@router.post("/create", response_model=dict)
async def create_question(question_data: dict = Body(openapi_examples=questions)) -> dict:
    return await question_service.create_question(question_data)

@router.get("/{question_id}", response_model=dict)
async def fetch_question(question_id: str) -> dict:
    return await question_service.fetch_question(question_id)

@router.put("/update/{question_id}", response_model=dict)
async def update_question(question_id: str, updated_data: QuestionUpdate) -> dict:
    return await question_service.update_question(question_id, updated_data)

@router.delete("/delete/{question_id}", response_model=dict)
async def delete_question(question_id: str) -> dict:
    return await question_service.delete_question(question_id)