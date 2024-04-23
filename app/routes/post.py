

from fastapi import APIRouter, Request, UploadFile, File,Form,HTTPException,Query
from fastapi.responses import JSONResponse
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, auth, storage
from fastapi import Request,HTTPException,Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import Request,HTTPException,Depends
import base64
import json
import binascii


router = APIRouter()
templates = Jinja2Templates(directory="templates")


db = firestore.client()

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


# Function to upload image to Firebase Storage
def upload_image(file: UploadFile):
    # Generate unique filename
    filename = f"Images/{datetime.now().strftime('%Y%m%d%H%M%S')}-{file.filename}"
    
    # Upload image to Firebase Storage
    bucket = storage.bucket()
    bucket = storage.bucket(app=firebase_admin.get_app(), name='assignment-c4726.appspot.com')

    bucket_name = bucket.name
    print("Firebase Storage Bucket Name:", bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_file(file.file)
    
    # Get download URL
    image_url = blob.public_url

    return image_url

# Route for creating a tweet
@router.post("/tweets")
async def create_tweet(request: Request,tweet: str = Form(...), image: UploadFile = File(None),current_user: dict = Depends(get_current_user)):
    # Get user ID from request headers
    uid = request.cookies.get("uid")

    if len(tweet) > 140:
            raise HTTPException(status_code=400, detail="Tweet content exceeds 140 characters")

    tweet_data = {
        "createdBy": uid,
        "display_name":current_user.get('display_name'),
        "createdAt": datetime.now(),
        "tweet": tweet,
        "likes": [],
    }

    if image:
        image_url = upload_image(image)
        tweet_data["imageUrl"] = image_url

    
    tweet_ref = db.collection("tweets").add(tweet_data)

 

    return {"message": "Tweet created successfully"}


@router.get("/tweets")
async def search_tweets(request: Request,query: str = Query(None)):
    try:
        uid = request.cookies.get('uid')
        token = request.cookies.get('token')

        if not token:
            return RedirectResponse(url="/auth/login")
        if query:
            tweets_ref = db.collection("tweets")
            tweet_docs = tweets_ref.stream()

            # Extract tweet data from documents
            tweets = []
            for doc in tweet_docs:
                tweet_data = doc.to_dict()
                tweet_data["id"] = doc.id
                if tweet_data["tweet"].startswith(query):  # Filter results to match beginning of content
                    tweets.append(tweet_data)

            return templates.TemplateResponse("tweet.html", {"request": request,"tweets": tweets,"uid":uid })
        else:
            # If no search query, return all tweets in descending order
            tweets_ref = db.collection("tweets")
            tweet_docs = tweets_ref.stream()

            # Extract tweet data from documents
            tweets = []
            for doc in tweet_docs:
                tweet_data = doc.to_dict()
                tweet_data["id"] = doc.id
                tweets.append(tweet_data)

            return templates.TemplateResponse("tweet.html", {"request": request,"tweets": tweets,"uid":uid  })

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.delete("/tweets/{tweet_id}")
async def delete_tweet(tweet_id: str):
    try:

        db.collection("tweets").document(tweet_id).delete()
        return {"message": "Tweet deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete tweet")