# app/routes/user.py
from fastapi import APIRouter,Query
from fastapi.responses import RedirectResponse
from fastapi import Request,HTTPException,Depends
from fastapi.templating import Jinja2Templates
import firebase_admin
from firebase_admin import credentials, auth,firestore
from datetime import datetime
import base64
import json
import binascii

templates = Jinja2Templates(directory="templates")

cred = credentials.Certificate('firebaseConfig.json') 
firebase_admin.initialize_app(cred,{'storageBucket': 'Images'})
db = firestore.client()

router = APIRouter()

def extract_name(email):
    if "@" in email:
        name_part = email.split("@")[0]
        return name_part.replace(".", " ").title()  # Convert to title case and replace dots with spaces
    else:
        return "Unknown"


def decode_jwt_token(token):
    try:
        # Split the token into header, payload, and signature parts
        header, payload, signature = token.split(".")

        # Decode the header and payload from base64
        decoded_header = base64.urlsafe_b64decode(header + "==").decode("utf-8")
        decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")

        # Parse the decoded JSON payload into a dictionary
        payload_dict = json.loads(decoded_payload)

        return payload_dict
    except (ValueError, binascii.Error, json.JSONDecodeError) as e:
        # Handle invalid or malformed tokens
        raise ValueError("Error decoding token:", e)


async def get_current_user(request: Request):
    try:
        # Get token from cookie
        token = request.cookies.get("token")
        if not token:
            return RedirectResponse(url="/")
        
        uid = request.cookies.get("uid")

        if not uid:
            decoded_token = decode_jwt_token(token)
            uid = decoded_token["user_id"]
            
        user_ref = db.collection("users").where("uid", "==", uid).limit(1)
        user_snapshot = user_ref.get()

        if not user_snapshot:
            return {}
        
        return user_snapshot[0].to_dict()  

    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/feed")
async def feed_page(request: Request):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/auth/login")
    
    decoded_token = decode_jwt_token(token)
    uid = decoded_token["user_id"]

    user_ref = db.collection("users").where("uid", "==", uid).limit(1)
    user_snapshot = user_ref.get()
    
    print('user_snapshot')
    print(user_snapshot)

    if not user_snapshot:
        return RedirectResponse(url="/user/setusername")
    # userData= user_snapshot[0].to_dict()  

    
    return templates.TemplateResponse("feed.html", {"request": request})




@router.get("/")
async def get_users(request: Request,username: str = Query(None), current_user: dict = Depends(get_current_user)):
    try:
        # Get display name of the current user
        uid = request.cookies.get("uid")
        print(username)

        if not username:
            users_ref = db.collection("users").where("uid", "!=", uid).stream()
            following_users = current_user.get("following", [])

            users = []
            for user_doc in users_ref:
                user_data = user_doc.to_dict()
                user_id = user_data.get("uid")
                user_data["follow"] = "unfollow" if user_id in following_users else "follow"
                users.append(user_data)
            
            return templates.TemplateResponse("users.html", {"request": request,"users": users })
        else:
            users_ref = db.collection("users").where("uid", "!=", uid).stream()
            following_users = current_user.get("following", [])

            users = []
            for doc in users_ref:
                user_data = doc.to_dict()
                user_id = user_data.get("uid")
                user_data["follow"] = "unfollow" if user_id in following_users else "follow"
        
                if user_data.get('display_name').startswith(username):
                     users.append(user_data)
            
            return templates.TemplateResponse("users.html", {"request": request,"users": users })

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/follow/{user_id}")
async def follow_user(request: Request,user_id: str, current_user: dict = Depends(get_current_user)):
    try:
        current_user_uid  = request.cookies.get("uid")

        following_users = current_user.get("following", [])
        action =''
        if user_id in following_users:
            following_users.remove(user_id)
            action = "unfollowed"
        else:
            following_users.append(user_id)
            action = "followed"

        # Update the following array in Firestore
        user_ref = db.collection("users").document(current_user_uid)
        user_ref.update({"following": following_users})

        return {"message": "Successfully {action} user with ID: {user_id}","action":action,"user_id":user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/add_user")
async def add_user(request: Request):
    # Get token from cookie
    token = request.cookies.get("token")
    request_body = await request.json()
        
    username = request_body.get("username")

    if not token:
        raise HTTPException(status_code=401, detail="Authorization token not provided")

    userexsist_ref = db.collection("users").where("display_name", "==", username).limit(1)
    user_snapshot = userexsist_ref.get()

    if user_snapshot:
        raise HTTPException(status_code=401, detail="username already exist, try again")

    
    try:
        decoded_token = decode_jwt_token(token)
        uid = decoded_token["user_id"]
        email = decoded_token["email"]
        display_name = username
        
        users_ref = db.collection("users")
        user_doc_ref = users_ref.document()

        user_data = {
            "uid": uid,
            "email": email,
            "createdAt": datetime.now(),
            "display_name": display_name if display_name else email.split("@")[0],
            "following" :[],
        }
        user_doc_ref.set(user_data)

        return {'message':'username added'}


    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/setusername")
async def setusername_page(request: Request, current_user: dict = Depends(get_current_user)):

    token = request.cookies.get('token')

    if not token:
        return RedirectResponse(url="/auth/login")

    if not current_user.get('display_name'):
        return templates.TemplateResponse("setusername.html", {"request": request})
    else:
        return RedirectResponse(url="/")


