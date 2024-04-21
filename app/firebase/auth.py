# firebase/auth.py

import firebase_admin
from firebase_admin import credentials

# Initialize Firebase Admin SDK
async def initialize_firebase():
    cred = credentials.Certificate("/twitter_project/firebaseConfig.json")  # Path to your Firebase service account key
    firebase_admin.initialize_app(cred)
