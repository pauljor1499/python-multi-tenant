from fastapi import HTTPException, Request
from bson import ObjectId
from src.connection import DATABASE, DB_CLIENT
from src.routes.accounts.models import SchoolAccount, SchoolAdminAccount, SchoolTeacherAccount, SchoolStudentAccount
from passlib.context import CryptContext
from src.authentication import jwt_handler

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AccountsService:
    def __init__(self):
        self.master_db = DATABASE
        self.client = DB_CLIENT

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    async def create_school_account(self, account_data: dict) -> dict:
        try:
            data_model = SchoolAccount(**account_data)
            result = await self.master_db["schools_collection"].insert_one(data_model.model_dump())

            school_db = self.client[data_model.code]
            existing_collections = await school_db.list_collection_names()
            collections_to_create = [
                "analytics_collection",
                "questions_collection",
                "assignments_collection",
                "classes_collection",
                "teacher_questionbank"
            ]
            for collection in collections_to_create:
                if collection not in existing_collections:
                    await school_db.create_collection(collection)

            return {"new_school_account_created": str(result.inserted_id)}
        except HTTPException as error:
            raise error
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while creating school account")


    async def create_school_admin_account(self, account_data: dict) -> dict:
        try:
            school = await self.master_db["schools_collection"].find_one({"name": account_data["school"]})
            if not school:
                raise HTTPException(status_code=404, detail="School not found. Cannot create admin account.")
            
            account_data["school"] = ObjectId(school["_id"])
            data_model = SchoolAdminAccount(**account_data)

            hashed_password = self.hash_password(data_model.password)
            account_data_dict = data_model.model_dump()
            account_data_dict["password"] = hashed_password

            result = await self.master_db["school_admins_collection"].insert_one(account_data_dict)
            return {"new_account_created": str(result.inserted_id)}
        except HTTPException as error:
            raise error
        
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while creating school admin account")


    async def login_school_admin_account(self, account_data: dict) -> dict:
        try:
            data_model = SchoolAdminAccount(**account_data)

            user = await self.master_db["school_admins_collection"].find_one({"email": data_model.email})

            if not user:
                raise HTTPException(status_code=404, detail="Account not found")
            
            if not pwd_context.verify(data_model.password, user["password"]):
                raise HTTPException(status_code=401, detail="Invalid password")
            
            school = await self.master_db["schools_collection"].find_one({"_id": user["school"]})
            if not school:
                raise HTTPException(status_code=404, detail="School not found")

            token = jwt_handler.signJWT(str(user["_id"]), str(user["role"]), str(school["code"]))
            return {"bearer_token": token}
        
        except HTTPException as error:
            raise error
        
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while logging in school admin account")

    

    async def create_teacher_account(self, account_data: dict) -> dict:
        try:
            school = await self.master_db["schools_collection"].find_one({"name": account_data["school"]})
            if not school:
                raise HTTPException(status_code=404, detail="School not found. Cannot create admin account.")
            
            account_data["school"] = ObjectId(school["_id"])
            data_model = SchoolTeacherAccount(**account_data)

            hashed_password = self.hash_password(data_model.password)
            account_data_dict = data_model.model_dump()
            account_data_dict["password"] = hashed_password

            result = await self.master_db["school_teachers_collection"].insert_one(account_data_dict)
            return {"new_account_created": str(result.inserted_id)}
        except HTTPException as error:
            raise error
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while creating school admin account")


    async def login_teacher_account(self, account_data: dict) -> dict:
        try:
            data_model = SchoolTeacherAccount(**account_data)

            user = await self.master_db["school_teachers_collection"].find_one({"email": data_model.email})

            if not user:
                raise HTTPException(status_code=404, detail="Account not found")
            
            if not pwd_context.verify(data_model.password, user["password"]):
                raise HTTPException(status_code=401, detail="Invalid password")
            
            school = await self.master_db["schools_collection"].find_one({"_id": user["school"]})
            if not school:
                raise HTTPException(status_code=404, detail="School not found")
            
            token = jwt_handler.signJWT(str(user["_id"]), str(user["role"]), str(school["code"]))
            return token
        
        except HTTPException as error:
            raise error
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while logging in school admin account")
    

    async def create_student_account(self, account_data: dict) -> dict:
        try:
            school = await self.master_db["schools_collection"].find_one({"name": account_data["school"]})
            if not school:
                raise HTTPException(status_code=404, detail="School not found. Cannot create admin account.")
            
            account_data["school"] = ObjectId(school["_id"])
            data_model = SchoolStudentAccount(**account_data)

            hashed_password = self.hash_password(data_model.password)
            account_data_dict = data_model.model_dump()
            account_data_dict["password"] = hashed_password
            
            result = await self.master_db["school_students_collection"].insert_one(account_data_dict)
            return {"new_account_created": str(result.inserted_id)}
        except HTTPException as error:
            raise error
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while creating school admin account")


    async def login_student_account(self, account_data: dict) -> dict:
        try:
            data_model = SchoolStudentAccount(**account_data)

            user = await self.master_db["school_students_collection"].find_one({"email": data_model.email})

            if not user:
                raise HTTPException(status_code=404, detail="Account not found")
            
            if not pwd_context.verify(data_model.password, user["password"]):
                raise HTTPException(status_code=401, detail="Invalid password")
            
            school = await self.master_db["schools_collection"].find_one({"_id": user["school"]})
            if not school:
                raise HTTPException(status_code=404, detail="School not found")
            
            token = jwt_handler.signJWT(str(user["_id"]), str(user["role"]), str(school["code"]))
            return token
        
        except HTTPException as error:
            raise error
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while logging in school admin account")


    
