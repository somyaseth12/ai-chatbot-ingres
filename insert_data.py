from pymongo import MongoClient
import json
from collections import defaultdict

client = MongoClient("mongodb://localhost:27017/")
db = client["groundwater_db"]
collection = db["data"]

collection.delete_many({})  # clear old data

with open("groundwater_data.json") as f:
    raw_data = json.load(f)

grouped = defaultdict(list)

for item in raw_data:
    key = (item["state"], item["district"])
    grouped[key].append({
        "year": item["year"],
        "extraction": item["extraction"],
        "recharge": item["recharge"],
        "category": item["category"]
    })

final_data = []

for (state, district), records in grouped.items():
    final_data.append({
        "state": state,
        "district": district,
        "records": sorted(records, key=lambda x: x["year"])
    })

collection.insert_many(final_data)

print("✅ Data inserted successfully")