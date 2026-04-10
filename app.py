from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()
VERIFY_TOKEN = os.getenv("verifytoken")
phone_id = os.getenv("whatsapp_phone_id")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  
##API_KEY = os.getenv("TWELVE_API_KEY")
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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""
You are a professional customer support assistant for Asterya store.

Business Info:
- we sell ethiopian opals fiery and non fiery grams ct averaging 35 ct or more based on demand 
- we also sell custom made jewelry with ethiopian opals and other gemstones
- we have a wide variety of ethiopian opals in different colors and sizes
- we have a team of expert gemologists who can help you find the perfect opal for your needs
- we offer competitive prices and excellent customer service
- Price range: $50-$200
- Location: Addis Ababa
- Shipping: Worldwide
- Return policy: 30 days
- Contact:daniel.mamo@asteryagemstone.com

Answer clearly and professionally only what is asked do not explain further.

User: {user_input}
"""
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        print("FULL AI RESPONSE:", result)

        # ✅ Correct parsing
        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("AI ERROR:", e)
        return "AI is currently unavailable."


@app.route("/webhook", methods=["GET", "POST"])


def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Verification failed", 403

def webhook():

    if request.method == 'GET':
     return "Webhook verified", 200
       
    if request.method == "POST":
    
        data = request.get_json()

    print("🔥 WEBHOOK HIT!")
    print("FULL DATA:", data)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" in value:
            message = value["messages"][0]["text"]["body"]
            sender = value["messages"][0]["from"]
            reply=faq_tool(message)or ai_response(message) or "I will connect you to customer support."
            send_whatsapp_message(sender, reply)
            print("USER:", message)
            print("SENDER:", sender)

    except Exception as e:
        print("ERROR:", e)

    return "ok"



def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{os.getenv('whatsapp_phone_id')}/messages"

    headers = {
        "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(url, headers=headers, json=data)

    # 🔥 Debug logs (VERY IMPORTANT)
    print("STATUS CODE:", response.status_code)
    print("WHATSAPP RESPONSE:", response.json())

    return response.json()





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