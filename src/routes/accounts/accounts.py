from fastapi import Request, APIRouter, Body
from src.routes.accounts.service import AccountsService


router = APIRouter()

account_service = AccountsService()

@router.post("/school/create", response_model=dict)
async def create_school_accounts(account_data: dict) -> dict:
    return await account_service.create_school_accounts(account_data)

# @router.post("/school-admin/create", response_model=dict)
# async def create_school_admin_account(account_data: dict) -> dict:
#     return await account_service.create_school_admin_account(account_data)

@router.post("/school-admin/login", response_model=dict)
async def login_school_admin_account(account_data: dict) -> dict:
    return await account_service.login_school_admin_account(account_data)

# @router.post("/teacher/create", response_model=dict)
# async def create_teacher_account(account_data: dict) -> dict:
#     return await account_service.create_teacher_accounts(account_data)

@router.post("/teacher/login", response_model=dict)
async def login_teacher_account(account_data: dict) -> dict:
    return await account_service.login_teacher_account(account_data)

# @router.post("/student/create", response_model=dict)
# async def create_student_account(account_data: dict) -> dict:
#     return await account_service.create_student_accounts(account_data)

@router.post("/student/login", response_model=dict)
async def login_student_account(account_data: dict) -> dict:
    return await account_service.login_student_account(account_data)