from fastapi import Request, APIRouter, Body, status, Depends
from src.routes.question_bank.service import QuestionBankService
from src.routes.question_bank.models import QuestionModelCreate, QuestionModelUpdate
from src.routes.question_bank.utilities.payloads import questions
from src.authentication.jwt_bearer import JWTBearer


router = APIRouter()

question_bank = QuestionBankService()

@router.get("", dependencies=[Depends(JWTBearer(access_levels=["teacher"]))], response_model=dict, status_code=status.HTTP_200_OK)
async def fetch_questions(request: Request) -> dict:
    query_dict = dict(request.query_params)
    return await question_bank.fetch_questions(query_dict, request)

@router.post("/create", dependencies=[Depends(JWTBearer(access_levels=["teacher"]))], response_model=dict, status_code=status.HTTP_200_OK)
async def create_question(request: Request, question_data: QuestionModelCreate = Body(openapi_examples=questions)) -> dict:
    return await question_bank.create_question(question_data, request)

@router.get("/{question_id}", dependencies=[Depends(JWTBearer(access_levels=["teacher"]))], response_model=dict, status_code=status.HTTP_200_OK)
async def fetch_question(request: Request, question_id: str) -> dict:
    return await question_bank.fetch_question(question_id, request)

@router.put("/update/{question_id}", dependencies=[Depends(JWTBearer(access_levels=["teacher"]))], response_model=dict, status_code=status.HTTP_200_OK)
async def update_question(request: Request, question_id: str, updated_data: QuestionModelUpdate) -> dict:
    return await question_bank.update_question(question_id, updated_data, request)

@router.delete("/delete/{question_id}", dependencies=[Depends(JWTBearer(access_levels=["teacher"]))], response_model=dict, status_code=status.HTTP_200_OK)
async def delete_question(request: Request, question_id: str) -> dict:
    return await question_bank.delete_question(question_id, request)