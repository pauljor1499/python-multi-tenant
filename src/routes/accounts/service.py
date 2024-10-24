from fastapi import HTTPException
from bson import ObjectId
from src.connection import DB_CLIENT
from src.routes.accounts.models import SchoolAdminAccount, SchoolAccount
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AccountsService:
    def __init__(self):
        self.client = DB_CLIENT

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    async def create_school_admin_account(self, account_data: dict) -> dict:
        try:
            data_model = SchoolAdminAccount(**account_data)
            hashed_password = self.hash_password(data_model.password)
            account_data_dict = data_model.model_dump()
            account_data_dict["password"] = hashed_password
            result = await self.client["prod-master"]["school_admin_collection"].insert_one(account_data_dict)
            return {"new_account_created": str(result.inserted_id)}
        except HTTPException as error:
            raise error
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while creating school admin account")


    async def login_school_admin_account(self, account_data: dict) -> dict:
        try:
            data_model = SchoolAdminAccount(**account_data)
            result = await self.client["prod-master"]["school_admin_collection"].find_one({"email": data_model.email})
            if not result:
                raise HTTPException(status_code=404, detail="Account not found")
            if not pwd_context.verify(data_model.password, result["password"]):
                raise HTTPException(status_code=401, detail="Invalid password")
            return {"message": "Login successful", "user_id": str(result["_id"])}
        except HTTPException as error:
            raise error
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while logging in school admin account")


    async def create_school_account(self, account_data: dict) -> dict:
        try:
            data_model = SchoolAccount(**account_data)
            result = await self.client["prod-master"]["school_collection"].insert_one(data_model.model_dump())

            school_db = self.client[data_model.school_code]
            await school_db.create_collection("analytics_collection")
            await school_db.create_collection("questions_collection")
            await school_db.create_collection("assignments_collection")

            return {"new_school_account_created": str(result.inserted_id)}
        except HTTPException as error:
            raise error
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while creating school account")
