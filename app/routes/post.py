# app/routes/post.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/feed")
def view_feed():
    pass
