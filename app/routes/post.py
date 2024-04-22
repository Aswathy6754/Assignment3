

from fastapi import APIRouter, Request, UploadFile, File,Form,HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, auth, storage

router = APIRouter()


db = firestore.client()


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
async def create_tweet(request: Request,tweet: str = Form(...), image: UploadFile = File(None)):
    # Get user ID from request headers
    uid = request.cookies.get("uid")

    if len(tweet) > 140:
            raise HTTPException(status_code=400, detail="Tweet content exceeds 140 characters")

    tweet_data = {
        "createdBy": uid,
        "createdAt": datetime.now(),
        "tweet": tweet,
        "likes": [],
    }

    if image:
        image_url = upload_image(image)
        tweet_data["imageUrl"] = image_url

    
    tweet_ref = db.collection("tweets").add(tweet_data)

 

    return {"message": "Tweet created successfully"}
