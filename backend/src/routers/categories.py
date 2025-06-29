from fastapi import APIRouter

from database.db_connection import DBConnection


router = APIRouter()


@router.get("/categories")
async def get_categories():
    categories_list =  DBConnection.find("categories", {})
    categories = []
    for category in categories_list:
        category["_id"] = str(category["_id"]) 
        categories.append(category)
    return categories
