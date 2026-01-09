from  fastapi import FastAPI

app = FastAPI()

book_db = {
    "id": int,
    "title": str,
    "author": str,
    "year_published": int,
    "genre": str,
    "is_read": bool
}
