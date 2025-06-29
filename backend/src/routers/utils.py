from datetime import date, datetime
from bson.objectid import ObjectId
from database.db_connection import DBConnection

def get_capsules_to_open(today: date):
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    print(start, end)
    capsules = list(DBConnection.find("capsule", {
        "send_date": {
            "$gte": start,
            "$lte": end
        }
    }))

    
    for capsule in capsules:
        user = DBConnection.find_one("users", {"_id": ObjectId(capsule["user_id"])})
        if user:
            capsule["user_email"] = user["email"]
            capsule["user_name"] = user.get("name", "Kullanıcı")
        else:
            capsule["user_email"] = "bilinmiyor"
            capsule["user_name"] = "bilinmiyor"

    return capsules
