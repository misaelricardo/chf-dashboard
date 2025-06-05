import pymongo
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["hf_monitoring_db"]
patients_collection = db["patients"]

# 🧹 Clear existing data
patients_collection.delete_many({})


