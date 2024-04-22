# app/routes/auth.py

from fastapi import APIRouter
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "form_type": 'login'})

@router.get("/signup")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "form_type": 'signup'})



@router.post("/signup")
def signup():
    pass

@router.post("/login")
def login():
    pass
