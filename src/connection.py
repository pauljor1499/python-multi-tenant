from motor.motor_asyncio import AsyncIOMotorClient
# from beanie import init_beanie
import os

MONGO_URL = os.getenv("MONGO_URL")
DB_CLIENT = AsyncIOMotorClient(MONGO_URL)

DB_MASTER = os.getenv("DB_MASTER")
DATABASE_MASTER = DB_CLIENT[DB_MASTER]

DB_USERS = os.getenv("DB_USERS")
DATABASE_USERS = DB_CLIENT[DB_USERS]

DB_GLOBAL_QUESTIONBANK = os.getenv("DB_GLOBAL_QUESTIONBANK")
DATABASE_GLOBAL_QUESTIONBANK = DB_CLIENT[DB_GLOBAL_QUESTIONBANK]

async def init_master_db():
    try:
        collections_to_create = [
            "schools_collection",
        ]
        existing_collections = await DATABASE_MASTER.list_collection_names()
        for collection in collections_to_create:
            if collection not in existing_collections:
                await DATABASE_MASTER.create_collection(collection)
            #     print(f"\033[32mINFO: Created collection: {collection}\033[0m")
            # else:
            #     print(f"\033[33mWARNING: Collection '{collection}' already exists.\033[0m")
        collections = await DATABASE_MASTER.list_collection_names()
        print(f"\033[32mINFO: Connected to the database: [{DB_MASTER}], collections: {collections}\033[0m")
    except Exception as e:
        print(f"\033[31mERROR: Unable to connect to the database.\033[0m")
        print(f"\033[31mERROR: {e}\033[0m")


async def init_users_db():
    try:
        collections_to_create = [
            "school_admins_collection",
            "school_teachers_collection",
            "school_students_collection",
        ]
        existing_collections = await DATABASE_USERS.list_collection_names()
        for collection in collections_to_create:
            if collection not in existing_collections:
                await DATABASE_USERS.create_collection(collection)
        collections = await DATABASE_USERS.list_collection_names()
        print(f"\033[32mINFO: Connected to the database: [{DB_USERS}], collections: {collections}\033[0m")
    except Exception as e:
        print(f"\033[31mERROR: Unable to connect to the database.\033[0m")
        print(f"\033[31mERROR: {e}\033[0m")


async def init_global_questionbank_db():
    try:
        collections_to_create = [
            "global_questionbank"
        ]
        existing_collections = await DATABASE_GLOBAL_QUESTIONBANK.list_collection_names()
        for collection in collections_to_create:
            if collection not in existing_collections:
                await DATABASE_GLOBAL_QUESTIONBANK.create_collection(collection)
        collections = await DATABASE_GLOBAL_QUESTIONBANK.list_collection_names()
        print(f"\033[32mINFO: Connected to the database: [{DB_GLOBAL_QUESTIONBANK}], collections: {collections}\033[0m")
    except Exception as e:
        print(f"\033[31mERROR: Unable to connect to the database.\033[0m")
        print(f"\033[31mERROR: {e}\033[0m")
