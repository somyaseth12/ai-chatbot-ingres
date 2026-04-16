import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# -------------------- FAQ PART (OLD) --------------------
if not os.path.exists("faq_data.json") or os.stat("faq_data.json").st_size == 0:
    import scrape_ingres_faq

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load FAQ data
with open("faq_data.json", "r") as f:
    faq_data = json.load(f)

if len(faq_data) == 0:
    raise ValueError("faq_data.json is empty. Run the scraper first.")

questions = [item["question"] for item in faq_data]
answers = [item["answer"] for item in faq_data]

# Convert questions to embeddings
embeddings = model.encode(questions, convert_to_numpy=True)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))


# -------------------- NEW: GROUNDWATER DATA PART --------------------

# Load groundwater data
with open("groundwater_data.json", "r") as f:
    groundwater_data = json.load(f)


def find_groundwater_data(district):
    for record in groundwater_data:
        if record["district"].lower() == district.lower():
            return record
    return None

def extract_district(query):
    query = query.lower()
    for record in groundwater_data:
        if record["district"].lower() in query:
            return record["district"]
    return None

def handle_groundwater_query(query):
    district = extract_district(query)
    state = extract_state(query)

    # 🎯 CASE 1: District found
    if district:
        data = find_groundwater_data(district)
        trend = get_trend(district)

        if data:
            return f"""
Groundwater in {data['district']} ({data['year']}):
Category: {data['category']}
Extraction: {data['extraction']}%
Recharge: {data['recharge']}

Trend: {trend}
"""
    
    # 🎯 CASE 2: Only state found
    elif state:
        records = [r for r in groundwater_data if r.get("state", "").lower() == state.lower()]

        if not records:
            return "No data found for this state."

        categories = [r["category"] for r in records if "category" in r]

        return f"""
Groundwater summary for {state}:
Areas include categories like: {", ".join(set(categories))}
"""

    # 🎯 CASE 3: Nothing found
    return "Please mention a valid district or state."

def extract_state(query):
    query = query.lower()

    # dataset se unique states nikaal lo
    states = list(set([r.get("state", "") for r in groundwater_data]))

    for state in states:
        if state.lower() in query:
            return state

    return None
def get_trend(district):
    records = [r for r in groundwater_data if r["district"].lower() == district.lower()]
    
    if len(records) < 2:
        return "Not enough data for trend analysis."

    records = sorted(records, key=lambda x: x["year"])

    first = records[0]["extraction"]
    last = records[-1]["extraction"]

    if last > first:
        return "Groundwater extraction is increasing 📈"
    elif last < first:
        return "Groundwater extraction is decreasing 📉"
    else:
        return "Groundwater extraction is stable"
def detect_intent(query):
    query = query.lower()

    if "trend" in query or "graph" in query:
        return "trend"
    elif "groundwater" in query or "water" in query:
        return "groundwater"
    else:
        return "faq"  
# -------------------- MAIN FUNCTION (UPDATED) --------------------

def get_response(user_query):
    intent = detect_intent(user_query)

    # 🎯 CASE 1: Groundwater Info
    if intent == "groundwater":
        return handle_groundwater_query(user_query)

    # 🎯 CASE 2: Trend Request
    elif intent == "trend":
        district = extract_district(user_query)

        if district:
            return f"Generating trend graph for {district} 📊"
        else:
            return "Please mention a district to show trend."

    # 🎯 CASE 3: FAQ (Fallback)
    else:
        query_embedding = model.encode([user_query])
        distances, indices = index.search(np.array(query_embedding), k=1)

        best_match = indices[0][0]
        return answers[best_match]