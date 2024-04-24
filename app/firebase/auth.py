# firebase/auth.py

from google.cloud import firestore 


# Initialize Firebase Admin SDK
async def initialize_firebase():
     db = firestore.Client()

