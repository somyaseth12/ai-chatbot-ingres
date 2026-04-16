from flask import Flask, request, jsonify, render_template
from chatbot_engine import get_response, extract_district, groundwater_data
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Ensure static folder exists
os.makedirs("static", exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


# 📊 Trend Chart API (AUTO DISTRICT DETECTION)
@app.route("/get-trend-chart", methods=["POST"])
def trend_chart():
    try:
        data = request.get_json()
        query = data.get("message", "").lower()

        # 🔥 Auto detect district from query
        district = extract_district(query)

        if not district:
            return jsonify({"error": "Please mention a valid district."})

        # Get records
        records = [r for r in groundwater_data if r["district"].lower() == district.lower()]
        
        if len(records) < 2:
            return jsonify({"error": "Not enough data for trend."})

        records = sorted(records, key=lambda x: x["year"])

        years = [r["year"] for r in records]
        extraction = [r["extraction"] for r in records]

        # Create graph
        plt.figure()
        plt.plot(years, extraction)
        plt.xlabel("Year")
        plt.ylabel("Extraction %")
        plt.title(f"Groundwater Trend - {district}")

        path = f"static/{district}_trend.png"
        plt.savefig(path)
        plt.close()

        return jsonify({"image": path})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Failed to generate chart."})


# 🤖 Chatbot API
@app.route("/get-response", methods=["POST"])
def chatbot_response():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"response": "Please send a valid message."})

        user_message = data["message"].strip()

        if user_message == "":
            return jsonify({"response": "Please ask something."})

        bot_response = get_response(user_message)

        return jsonify({"response": bot_response})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"response": "Something went wrong. Please try again."})


if __name__ == "__main__":
    app.run(debug=True)