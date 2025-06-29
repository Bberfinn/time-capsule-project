from fastapi import HTTPException
import pymongo


class DBConnection:
    URI: str = "mongodb://127.0.0.1:27017"
    DATABASE: None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(DBConnection.URI)
        DBConnection.DATABASE = client["company"]

    @staticmethod
    def insert(collection, data):
        if DBConnection.DATABASE is None:
            raise HTTPException(status_code=400, detail="Database Yok")
        return DBConnection.DATABASE[collection].insert_one(data)
    
    @staticmethod
    def delete(collection, query):
        if DBConnection.DATABASE is None:
            raise HTTPException(status_code=400, detail="Database Yok")
        return DBConnection.DATABASE[collection].delete_many(query)
    
    @staticmethod
    def find_one(collection, query):
        if DBConnection.DATABASE is None:
            raise HTTPException(status_code=400, detail="Database Yok")
        return DBConnection.DATABASE[collection].find_one(query)
    
    @staticmethod
    def find(collection, query):
        if DBConnection.DATABASE is None:
            raise HTTPException(status_code=400, detail="Database Yok")
        return DBConnection.DATABASE[collection].find(query)
    
    @staticmethod
    def update_one(collection, query, data):
        if DBConnection.DATABASE is None:
            raise HTTPException(status_code=400, detail="Database Yok")
        return DBConnection.DATABASE[collection].update_one(query, data)
    
    @staticmethod
    def update_many(collection, query, data):
        if DBConnection.DATABASE is None:
            raise HTTPException(status_code=400, detail="Database Yok")
        return DBConnection.DATABASE[collection].update_many(query, data)
    

    @staticmethod
    def delete_one(collection, query):
       if DBConnection.DATABASE is None:
         raise HTTPException(status_code=400, detail="Database Yok")
       return DBConnection.DATABASE[collection].delete_one(query)
