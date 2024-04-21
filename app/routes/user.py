# app/routes/user.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/search")
def search_users():
    pass

@router.post("/follow")
def follow_user():
    pass

@router.post("/unfollow")
def unfollow_user():
    pass
