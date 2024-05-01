from fastapi import FastAPI, Request , HTTPException,UploadFile, Depends, File,Form,Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import firestore , storage
from google.auth.transport import requests
from datetime import datetime
import base64
import json
import binascii
import mimetypes


app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# Initialize Firebase Admin SDK
db = firestore.Client()



@app.get("/")
async def feed_page(request: Request):
    return RedirectResponse(url="/user/feed")
    

@app.get("/auth/login")
async def login_page(request: Request):
    token = request.cookies.get('token')

    if  token:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("login.html", {"request": request, "form_type": 'login'})

@app.get("/auth/signup")
async def login_page(request: Request):
    token = request.cookies.get('token')

    if  token:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("login.html", {"request": request, "form_type": 'signup'})


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
        
        decoded_token = decode_jwt_token(token)
        uid = decoded_token["user_id"]
        
        user_ref = db.collection("users").where("uid", "==", uid).limit(1)
        user_snapshot = user_ref.get()

        if not user_snapshot:
            return {}
        
        return user_snapshot[0].to_dict()  

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/user/feed")
async def feed_page(request: Request):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/auth/login")
    
    decoded_token = decode_jwt_token(token)
    uid = decoded_token["user_id"]

    user_ref = db.collection("users").where("uid", "==", uid).limit(1)
    user_snapshot = user_ref.get()
 
  
    if not user_snapshot:
        return RedirectResponse(url="/user/setusername")
    
    try:

        user_data = user_snapshot[0].to_dict()
        following_uids = [uid]  # Initialize with current user's UID
        if "following" in user_data:
            following_uids.extend(user_data["following"])

        tweets_ref = db.collection("tweets").where("createdBy", "in", following_uids)
        tweet_docs = tweets_ref.stream()
        tweets = []
        for doc in tweet_docs:
            tweet_data = doc.to_dict()
            tweet_data["id"] = doc.id
            tweets.append(tweet_data)
        
        print(tweets)
        return templates.TemplateResponse("feed.html", {"request": request, "tweets": tweets,"uid":uid})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/user")
async def get_users(request: Request,username: str = Query(None), current_user: dict = Depends(get_current_user)):
    try:
        # Get display name of the current user
        uid = request.cookies.get("uid")
        token = request.cookies.get('token')

        if not token:
            return RedirectResponse(url="/auth/login")
        
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

@app.post("/user/follow/{user_id}")
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

        query_ref = db.collection('users').where('uid', '==', current_user_uid).limit(1)
        docs = query_ref.stream()

        # Check if document exists
        for doc in docs:
            doc_ref = db.collection('users').document(doc.id)
            doc_ref.update({"following": following_users})

            return {"message": "Successfully {action} user with ID: {user_id}","action":action,"user_id":user_id}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/user/add_user")
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


    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/user/setusername")
async def setusername_page(request: Request, current_user: dict = Depends(get_current_user)):

    token = request.cookies.get('token')

    if not token:
        return RedirectResponse(url="/auth/login")
    if not current_user.get('display_name'):
        return templates.TemplateResponse("setusername.html", {"request": request})
    else:
        return RedirectResponse(url="/")


@app.get("/user/profile/{user_uid}")
async def profile_page(request: Request,user_uid: str,current_user: dict = Depends(get_current_user)):

    token = request.cookies.get('token')

    if not token:
        return RedirectResponse(url="/auth/login")
    else:


        
        query_ref = db.collection('users').where('uid', '==', user_uid).limit(1)
        user_snapshot = query_ref.get()

        if not user_snapshot:
            raise HTTPException(status_code=401, detail="user not exist")

        following_users = current_user.get("following", [])
        button =''
        if user_uid in following_users:
            button = "unfollow"
        else :
            button = "follow"

        user_details = user_snapshot[0].to_dict()

        tweet_query_ref = db.collection('tweets').where('createdBy', '==', user_uid).limit(10)
        tweet_snapshot = tweet_query_ref.get()

        tweets = []
        for tweet in tweet_snapshot:
                tweet_data = tweet.to_dict()
                tweets.append(tweet_data)

        print(user_details,button,tweets)
        return templates.TemplateResponse("profile.html", {"request": request,"user_details":user_details,"button":button,"tweets":tweets})

# Function to upload image to Firebase Storage
def upload_image(file: UploadFile):
    # Generate unique filename
    if not file.filename :
        return ""

    filename = f"Images/{datetime.now().strftime('%Y%m%d%H%M%S')}-{file.filename}"
    
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = "application/octet-stream"
    print(mime_type)
    client = storage.Client()

    bucket = client.get_bucket("assignment-c4726.appspot.com")

    bucket_name = bucket.name
    print("Firebase Storage Bucket Name:", bucket_name)
    blob = bucket.blob(filename)
    blob.make_public()
    blob.upload_from_file(file.file,content_type=mime_type)
    
    # Get download URL
    image_url = blob.public_url

    return image_url

@app.get("/post/edit/{tweet_id}")
async def edittweet_page(request: Request,tweet_id: str,current_user: dict = Depends(get_current_user)):

    token = request.cookies.get('token')

    if not token:
        return RedirectResponse(url="/auth/login")
    else:
        tweet_query_ref = db.collection('tweets').document(tweet_id)
        tweet_snapshot = tweet_query_ref.get()
        if not tweet_snapshot.exists:
            return RedirectResponse(url="/")

        tweet_data = tweet_snapshot.to_dict()

        return templates.TemplateResponse("tweetedit.html", {"request": request,"tweet":tweet_data})

@app.put("/post/edit/{tweet_id}")
async def update_tweet(tweet_id: str, request: Request, tweet: str = Form(...), image: UploadFile = File(None)):
    try:
        tweet_ref = db.collection("tweets").document(tweet_id)

        tweet_snapshot = tweet_ref.get()
        if not tweet_snapshot.exists:
            raise HTTPException(status_code=404, detail="Tweet not found")

        update_data = {}
        if tweet:
            update_data["tweet"] = tweet
        
        # Upload the image file and update the image URL if provided
        if image:
            image_url = upload_image(image)
            update_data["imageUrl"] = image_url

        # Update the tweet document
        tweet_ref.update(update_data)

        return {"message": "Tweet updated successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

# Route for creating a tweet
@app.post("/post/tweets")
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
        "imageUrl":""
    }

    if image:
        image_url = upload_image(image)
        tweet_data["imageUrl"] = image_url

    
    tweet_ref = db.collection("tweets").add(tweet_data)

 

    return {"message": "Tweet created successfully"}


@app.get("/post/tweets")
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
    

@app.delete("/post/tweets/{tweet_id}")
async def delete_tweet(tweet_id: str):
    try:
        db.collection("tweets").document(tweet_id).delete()
        return {"message": "Tweet deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete tweet")