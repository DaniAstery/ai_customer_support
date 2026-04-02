from flask import CORS,Flask
from dotenv import load_dotenv
import os
import requests

load_dotenv()
API_KEY = os.getenv("TWELVE_API_KEY")

app = Flask(__name__)
CORS(app)

# 🔥 Global memory
messages = []
state = {}

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

# 🔥 Binance tool
def binance_tool(user_input):
    user_input = user_input.lower()
    coins = {"btc": "BTC/USD", "eth": "ETH/USD", "sol": "SOL/USD"}

    for coin in coins:
        if coin in user_input and "price" in user_input:
            try:
                url = f"https://api.twelvedata.com/price?symbol={coins[coin]}&apikey={API_KEY}"
                data = requests.get(url).json()
                price = float(data["price"])
                return f"{coin.upper()} price: ${price}"
            except:
                return "Error fetching price"

    if "price" in user_input and not any(c in user_input for c in coins):
        state["awaiting_coin"] = True
        return "Which coin? (btc, eth, sol)"

    if state.get("awaiting_coin"):
        if user_input in coins:
            state["awaiting_coin"] = False
            try:
                url = f"https://api.twelvedata.com/price?symbol={coins[user_input]}&apikey={API_KEY}"
                data = requests.get(url).json()
                price = float(data["price"])
                return f"{user_input.upper()} price: ${price}"
            except:
                return "Error fetching price"

    return None

# 🔥 FAQ tool
def faq_tool(user_input):
    user_input = user_input.lower()
    for faq in faqs:
        if faq["question"] in user_input:
            return faq["answer"]
    return None

# ✅ Health route (IMPORTANT)
@app.route("/")
def home():
    return "API is running"

# ✅ Chat route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")

    tool_result = binance_tool(user_input)

    if tool_result:
        reply = tool_result
    else:
        faq_result = faq_tool(user_input)
        if faq_result:
            reply = faq_result
        else:
            reply = "I will connect you to customer support."

    return jsonify({"reply": reply})

# 🔥 Only for local
if __name__ == "__main__":
    app.run(debug=True)