from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()
API_KEY = os.getenv("TWELVE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)

# ✅ Proper CORS configuration for production
CORS(app, resources={r"/*": {"origins": "*"}})

# 🔥 FAQ list
faqs = [
    {"question": "what are your hours", "answer": "We are open from 9 AM to 6 PM."},
    {"question": "where are you located", "answer": "We are located in Addis Ababa."},
    {"question": "how can i contact you", "answer": "Email us at support@example.com."},
    {"question": "what services do you offer", "answer": "We offer web development, digital marketing, and graphic design."},
    {"question": "do you have any discounts", "answer": "Yes, we offer seasonal discounts."},
    {"question": "return policy", "answer": "Returns are accepted within 30 days."},
    {"question": "international shipping", "answer": "Yes, we offer international shipping."}
]

# 🔥 Binance tool (Commented out as requested)
# def binance_tool(user_input):
#     user_input = user_input.lower()
#     coins = {"btc": "BTC/USD", "eth": "ETH/USD", "sol": "SOL/USD"}
#
#     for coin in coins:
#         if coin in user_input and "price" in user_input:
#             try:
#                 url = f"https://api.twelvedata.com/price?symbol={coins[coin]}&apikey={API_KEY}"
#                 response = requests.get(url)
#                 data = response.json()
#
#                 if "price" not in data:
#                     return "API error or invalid API key"
#
#                 price = float(data["price"])
#                 return f"{coin.upper()} price: ${price}"
#
#             except Exception as e:
#                 print("ERROR:", e)
#                 return "Error fetching price"
#     return None

# 🔥 FAQ tool

def faq_tool(user_input):
    user_input = user_input.lower()
    for faq in faqs:
        if faq["question"] in user_input:
            return faq["answer"]
    return None

def ai_response(user_input):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""
You are a customer support assistant for Asterya store.

Business Information:
- We sell watches and jewelry
- Price range: $50 - $200
- Location: Addis Ababa
- Shipping: Worldwide
- Return policy: 30 days
- Contact: support@example.com

Instructions:
- Answer like a professional support agent
- Be clear and helpful
- If unsure, say you will confirm you can reach out to the customer support team and get back to them via email daniel.mamo@asteryagemstone.com.

User question:
{user_input}
"""
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("AI ERROR:", e)
        return "AI is currently unavailable."




# ✅ Combined Route to prevent 405 Errors
# This handles the landing page (GET) and the chat logic (POST) in one place.
@app.route("/chat", methods=["GET", "POST", "OPTIONS"])
def handle_request():
    # Handle CORS Preflight
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    # Handle Health Check (Standard browser visit)
    if request.method == "GET":
        return "Chatbot API is active. Send a POST request to interact."

    # Handle Chat Logic
    try:
        data = request.get_json()
        if not data:
            return jsonify({"reply": "No data provided"}), 400

        user_input = data.get("message", "").lower()

        # Check FAQ tool
        faq_result = faq_tool(user_input)
        if faq_result:
            return jsonify({"reply": faq_result})
        
        # Check AI tool    
        
        ai_reply = ai_response(user_input)
        if ai_reply:
            return jsonify({"reply": ai_reply})    

        # Default fallback
        return jsonify({"reply": "I will connect you to customer support."})

    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return jsonify({"reply": "Server error. Please try again later."}), 500

# 🔥 Production configuration for Render
if __name__ == "__main__":
    # Render provides a PORT environment variable. If not found, it defaults to 5000.
    port = int(os.environ.get("PORT", 5000))
    # host="0.0.0.0" is required for the service to be accessible externally.
    app.run(host="0.0.0.0", port=port)