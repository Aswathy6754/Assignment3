# app/routes/user.py
from fastapi import APIRouter
from fastapi import Request
from fastapi.templating import Jinja2Templates
import firebase_admin
from firebase_admin import credentials, auth

templates = Jinja2Templates(directory="templates")

cred = credentials.Certificate('firebaseConfig.json') 
firebase_admin.initialize_app(cred)

router = APIRouter()

def extract_name(email):
    if "@" in email:
        name_part = email.split("@")[0]
        return name_part.replace(".", " ").title()  # Convert to title case and replace dots with spaces
    else:
        return "Unknown"


@router.get("/")
async def users_page(request: Request):

    all_users = []
    page = auth.list_users()
    for user in page.iterate_all():
        user_data = {
            "uid": user.uid,
            "email": user.email,
            "photo_url": user.photo_url,
            "display_name": extract_name(user.email)
        }
        all_users.append(user_data)

    return templates.TemplateResponse("users.html", {"request": request,"users": all_users })

@router.get("/search")
def search_users():
    pass

@router.post("/follow")
def follow_user():
    pass

@router.post("/unfollow")
def unfollow_user():
    pass
