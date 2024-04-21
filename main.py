from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi import Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.routes import auth ,user
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# Include the auth router as a nested router
app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, prefix="/user")



@app.get("/")
async def feed_page(request: Request):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/auth/login")
    
    return templates.TemplateResponse("feed.html", {"request": request})