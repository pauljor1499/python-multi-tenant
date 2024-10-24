from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional

def question_serializer(question: dict) -> dict:
    return {
        "_id": str(question["_id"]),
        "question": question["question"], #required
        "choices": question.get("choices"), #optional (with get is optional)
        "correctAnswer": question["correctAnswer"],
        "questionDetails": question.get("questionDetails"),
        "assignmentType": question["assignmentType"],
        "questionType": question["questionType"],
        "difficulty": question.get("difficulty"),
        "teksCode": question["teksCode"],
        "points": question["points"],
        "category": question["category"]
    }


class QuestionService:
    def __init__(self, db_client: str):
        self.client = AsyncIOMotorClient(db_client)
        self.db = self.client["teacher-questionbank"]
        self.collection = self.db["questionbank"]
        if self.client is None:
            print("Failed to connect to MongoDB.")
        else:
            print("Connected to MongoDB.")


    async def create_question(self, question_data: dict) -> str:
        """Create a new question and return its ID."""
        result = await self.collection.insert_one(question_data)
        return await self.fetch_question(result.inserted_id)


    async def fetch_question(self, question_id: str) -> Optional[dict]:
        """Fetch a single question by its ID."""
        question = await self.collection.find_one({"_id": ObjectId(question_id)})
        return question_serializer(question) if question else None


    async def update_question(self, question_id: str, question_data: dict) -> Optional[dict]:
        """Update an existing question by its ID and return the updated question."""
        result = await self.collection.update_one(
            {"_id": ObjectId(question_id)},
            {"$set": question_data}
        )
        return await self.fetch_question(question_id) if result.modified_count else None


    async def delete_question(self, question_id: str) -> bool:
        """Delete a question by its ID and return a boolean indicating success."""
        question = await self.fetch_question(question_id)
        result = await self.collection.delete_one({"_id": ObjectId(question_id)})
        return {"deleted": result.deleted_count > 0, "data": question}


    async def fetch_questions(self, question_type: Optional[str] = None, assignment_type: Optional[str] = None, category: Optional[str] = None, difficulty: Optional[str] = None,page: Optional[int] = 1, page_size: Optional[int] = 10) -> List[dict]:
        """Fetch all questions, optionally filtered, and count by assignmentType, questionType, category, and difficulty with pagination."""
        
        # Calculate skip and limit for pagination
        skip = (page - 1) * page_size
        limit = page_size
        
        # Create a match criteria based on provided filters
        match_criteria = {}
        if question_type is not None:
            match_criteria["questionType"] = question_type
        if assignment_type is not None:
            match_criteria["assignmentType"] = assignment_type
        if category is not None:
            match_criteria["category"] = category
        if difficulty is not None:
            match_criteria["difficulty"] = difficulty

        # Fetch total number of questions matching the criteria (overall number of questions)
        total_questions = await self.collection.count_documents(match_criteria)
        
        # Create the aggregation pipeline for counting
        pipeline = []
        if match_criteria:
            pipeline.append({"$match": match_criteria})

        # Add a group stage to count questions by assignment type, question type, category, and difficulty
        pipeline.append({
            "$group": {
                "_id": {
                    "assignmentType": "$assignmentType",
                    "questionType": "$questionType",
                    "category": "$category",
                    "difficulty": "$difficulty"
                },
                "count": {"$sum": 1}
            }
        })

        try:
            # Fetch assignment type, question type, category, and difficulty counts
            counts = await self.collection.aggregate(pipeline).to_list(100)

            # Prepare containers for different counts
            assignment_types_counts = {
                "STAAR": 0,
                "TSI": 0,
                "SAT": 0,
                "ACT": 0,
            }
            question_types_counts = {}
            categories_counts = {}
            difficulties_counts = {}

            # Process the results to get counts for each field
            for item in counts:
                # Unpack the fields from the group result
                assignment_type = item["_id"]["assignmentType"]
                question_type = item["_id"]["questionType"]
                category = item["_id"]["category"]
                difficulty = item["_id"]["difficulty"]
                count = item["count"]

                # Update assignment type counts
                if assignment_type in assignment_types_counts:
                    assignment_types_counts[assignment_type] += count

                # Update question type counts
                if question_type:
                    question_types_counts[question_type] = question_types_counts.get(question_type, 0) + count

                # Update category counts
                if category:
                    categories_counts[category] = categories_counts.get(category, 0) + count

                # Update difficulty counts
                if difficulty:
                    difficulties_counts[difficulty] = difficulties_counts.get(difficulty, 0) + count

        except Exception as e:
            print(f"Error counting assignment types, question types, categories, or difficulties: {e}")
            assignment_types_counts = {key: 0 for key in assignment_types_counts}
            question_types_counts = {}
            categories_counts = {}
            difficulties_counts = {}

        # Create a match criteria for fetching the questions
        questions_pipeline = []
        if match_criteria:
            questions_pipeline.append({"$match": match_criteria})

        # Add skip and limit for pagination
        questions_pipeline.append({"$skip": skip})
        questions_pipeline.append({"$limit": limit})

        # Fetch questions based on the same criteria
        try:
            questions = await self.collection.aggregate(questions_pipeline).to_list(100)
            question_list = [question_serializer(question) for question in questions]
        except Exception as e:
            print(f"Error fetching questions: {e}")
            question_list = []

        # Return the structured data with pagination information
        return {
            "data": {
                "questions": question_list,
                "assignmentTypes": assignment_types_counts,
                "questionTypes": question_types_counts,
                "categories": categories_counts,
                "difficulties": difficulties_counts,
            },
            "pagination": {
                "page": page,
                "pageSize": page_size,
                "totalCount": len(question_list),  # Total count of fetched questions on the current page
                "totalQuestions": total_questions
            }
        }