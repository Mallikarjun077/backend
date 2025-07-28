from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client["matri"]
users = db["users"]
profiles = db["profiles"]
pre_profiles = db["pre_profiles"]  # For pre-registration profiles
masters = db["masters"]            # ⬅️ Add this line for Master Data

# ✅ Insert religion master
masters.insert_one({
    "type": "religion",
    "values": ["Hindu", "Muslim", "Christian", "Sikh", "Jain", "Other"]
})

# ✅ Insert caste master
masters.insert_one({
    "type": "caste",
    "values": ["Brahmin", "Kshatriya", "Vaishya", "Shudra", "Other"]
})

# ✅ Insert job sector master
masters.insert_one({
    "type": "job_sector",
    "values": ["Government", "Private", "Business", "Defence", "Other"]
})

# ✅ Insert education qualification master
masters.insert_one({
    "type": "qualification",
    "values": ["B.Tech", "M.Tech", "MBA", "MBBS", "CA", "Diploma", "Other"]
})

# ✅ Insert eating habits
masters.insert_one({
    "type": "eating_habits",
    "values": ["Vegetarian", "Non-Vegetarian", "Eggetarian", "Vegan"]
})

# ✅ Insert annual income
masters.insert_one({
    "type": "annual_income",
    "values": [
        "Below ₹2 Lakh", 
        "₹2 - ₹5 Lakh", 
        "₹5 - ₹10 Lakh", 
        "₹10 - ₹25 Lakh", 
        "₹25 Lakh - ₹50 Lakh", 
        "Above ₹50 Lakh"
    ]
})

# ✅ Insert country
masters.insert_one({
    "type": "country",
    "values": ["India", "USA", "UK", "Canada", "Australia", "Other"]
})

# ✅ Insert state
masters.insert_one({
    "type": "state",
    "values": ["Karnataka", "Maharashtra", "Tamil Nadu", "Telangana", "Delhi", "Other"]
})

# ✅ Insert city
masters.insert_one({
    "type": "city",
    "values": ["Bangalore", "Mumbai", "Chennai", "Hyderabad", "Delhi", "Other"]
})

# ✅ Insert gender
masters.insert_one({
    "type": "gender",
    "values": ["Male", "Female", "Other"]
})

# ✅ Insert mother tongue / language
masters.insert_one({
    "type": "language",
    "values": ["Kannada", "Hindi", "Telugu", "Tamil", "Marathi", "Malayalam", "English", "Urdu", "Other"]
})

masters.insert_one({
    "type": "age",
    "values": [
        "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
        "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43",
        "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56",
        "57", "58", "59", "60"
    ]
})

# ✅ Insert mother tongue master
masters.insert_one({
    "type": "mother_tongue",
    "values": [
        "Hindi", "English", "Kannada", "Telugu", "Tamil", "Malayalam",
        "Marathi", "Gujarati", "Punjabi", "Bengali", "Urdu", "Odia",
        "Assamese", "Rajasthani", "Sindhi", "Konkani", "Tulu", "Other"
    ]
})
