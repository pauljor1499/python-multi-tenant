from fastapi import HTTPException, Request
from bson import ObjectId
from src.connection import DB_CLIENT, DATABASE_MASTER, DATABASE_USERS, DATABASE_GLOBAL_QUESTIONBANK
from src.routes.accounts.models import SchoolAccount, SchoolAdminAccount, SchoolTeacherAccount, SchoolStudentAccount
from passlib.context import CryptContext
from src.authentication import jwt_handler

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AccountsService:
    def __init__(self):
        self.master_db = DATABASE_MASTER
        self.users_db = DATABASE_USERS
        self.global_question_bank = DATABASE_GLOBAL_QUESTIONBANK
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
                "feature_flags_collection",
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

            user = await self.users_db["school_admins_collection"].find_one({"email": data_model.email})

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

    

    async def create_teacher_accounts(self, account_data: dict) -> dict:
        try:
            school = await self.master_db["schools_collection"].find_one({"name": account_data["school"]})
            if not school:
                raise HTTPException(status_code=404, detail="School not found. Cannot create teacher accounts.")
            
            created_accounts = []

            for teacher_data in account_data["teachers_list"]:
                teacher_data["school"] = ObjectId(school["_id"])
                data_model = SchoolTeacherAccount(**teacher_data)

                hashed_password = self.hash_password(data_model.password)
                teacher_account_data = data_model.model_dump()
                teacher_account_data["password"] = hashed_password

                result = await self.master_db["school_teachers_collection"].insert_one(teacher_account_data)
                created_accounts.append(str(result.inserted_id))
            
            return {"school": school["name"],"new_accounts_created": created_accounts}

        except HTTPException as error:
            raise error
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while creating teacher accounts")


    async def login_teacher_account(self, account_data: dict) -> dict:
        try:
            data_model = SchoolTeacherAccount(**account_data)

            user = await self.users_db["school_teachers_collection"].find_one({"email": data_model.email})

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
    

    async def create_student_accounts(self, account_data: dict) -> dict:
        try:
            school = await self.master_db["schools_collection"].find_one({"name": account_data["school"]})
            if not school:
                raise HTTPException(status_code=404, detail="School not found. Cannot create teacher accounts.")
            
            created_accounts = []

            for student_data in account_data["students_list"]:
                student_data["school"] = ObjectId(school["_id"])
                data_model = SchoolStudentAccount(**student_data)

                hashed_password = self.hash_password(data_model.password)
                student_account_data = data_model.model_dump()
                student_account_data["password"] = hashed_password

                result = await self.master_db["school_students_collection"].insert_one(student_account_data)
                created_accounts.append(str(result.inserted_id))
            
            return {"school": school["name"],"new_accounts_created": created_accounts}
        except HTTPException as error:
            raise error
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while creating school admin account")


    async def login_student_account(self, account_data: dict) -> dict:
        try:
            data_model = SchoolStudentAccount(**account_data)

            user = await self.users_db["school_students_collection"].find_one({"email": data_model.email})

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
    

    async def create_school_accounts(self, account_data: dict) -> dict:
        try:
            # Check if school already exists
            existing_school = await self.master_db["schools_collection"].find_one({"name": account_data["school"]["name"]})
            if existing_school:
                raise HTTPException(status_code=409, detail="School already registered.")

            # Insert school record into the master database
            school_model = SchoolAccount(**account_data["school"])
            school_insert_result = await self.master_db["schools_collection"].insert_one(school_model.model_dump())

            school_db = self.client[school_model.code]
            existing_collections = await school_db.list_collection_names()
            collections_to_create = [
                "feature_flags_collection",
                "analytics_collection",
                "questions_collection",
                "assignments_collection",
                "classes_collection",
                "teacher_questionbank"
            ]
            for collection in collections_to_create:
                if collection not in existing_collections:
                    await school_db.create_collection(collection)

            # Get the created school's ID to reference in related accounts
            school_id = school_insert_result.inserted_id
            created_accounts = {
                "school": str(school_id),
                "admin": None,
                "teachers": [],
                "students": []
            }

            # Create the admin account
            admin_data = account_data["admin"]
            admin_data["role"] = "school-admin"
            admin_data["school"] = school_id
            data_model = SchoolAdminAccount(**admin_data)
            account_data_dict = data_model.model_dump()
            account_data_dict["password"] = self.hash_password(data_model.password)

            admin_insert_result = await self.users_db["school_admins_collection"].insert_one(account_data_dict)
            created_accounts["admin"] = str(admin_insert_result.inserted_id)

            # Create teacher accounts
            for teacher_data in account_data["teachers_list"]:
                teacher_data["school"] = school_id
                teacher_model = SchoolTeacherAccount(**teacher_data)
                teacher_data_dict = teacher_model.model_dump()
                teacher_data_dict["password"] = self.hash_password(teacher_model.password)

                teacher_insert_result = await self.users_db["school_teachers_collection"].insert_one(teacher_data_dict)
                created_accounts["teachers"].append(str(teacher_insert_result.inserted_id))

            # Create student accounts
            for student_data in account_data["students_list"]:
                student_data["school"] = school_id
                student_model = SchoolStudentAccount(**student_data)
                student_data_dict = student_model.model_dump()
                student_data_dict["password"] = self.hash_password(student_model.password)

                student_insert_result = await self.users_db["school_students_collection"].insert_one(student_data_dict)
                created_accounts["students"].append(str(student_insert_result.inserted_id))

            return created_accounts

        except HTTPException as error:
            raise error
        except Exception as e:
            print(f"\033[31mERROR: {e}\033[0m")
            raise HTTPException(status_code=500, detail="Error while creating school accounts")


    
