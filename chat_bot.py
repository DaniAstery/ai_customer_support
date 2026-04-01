from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests

load_dotenv()
API_KEY = os.getenv("TWELVE_API_KEY")

app = Flask(__name__)

# Conversation memory
messages = []
state = {}

# FAQ list
faqs = [
    {"question": "what are your hours", "answer": "We are open from 9 AM to 6 PM."},
    {"question": "where are you located", "answer": "We are located in Addis Ababa."},
    {"question": "how can i contact you", "answer": "Email us at support@example.com."},
    {"question": "what services do you offer", "answer": "We offer web development, digital marketing, and graphic design."},
    {"question": "do you have any discounts", "answer": "Yes, we offer seasonal discounts. Check our website for the latest offers."},
    {"question": "what is your return policy", "answer": "Returns are accepted within 30 days with a valid receipt."},
    {"question": "do you offer international shipping", "answer": "Yes, shipping fees and delivery times vary based on location."}
]

# 🔥 Tool: Binance price checker
def binance_tool(user_input):
    user_input = user_input.lower()
    coins = {"btc": "BTC/USD", "eth": "ETH/USD", "sol": "SOL/USD"}

    # Check if coin and price mentioned
    for coin in coins:
        if coin in user_input and "price" in user_input:
            try:
                symbol = coins[coin]
                url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
                resp = requests.get(url).json()
                price = float(resp["price"])
                return f"{coin.upper()} price: ${price}"
            except:
                return "Error fetching price"

    # Awaiting coin selection
    if "price" in user_input and not any(c in user_input for c in coins):
        state["awaiting_coin"] = True
        return "Which coin? (btc, eth, sol)"

    if state.get("awaiting_coin"):
        if user_input in coins:
            state["awaiting_coin"] = False
            try:
                symbol = coins[user_input]
                url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
                resp = requests.get(url).json()
                price = float(resp["price"])
                return f"{user_input.upper()} price: ${price}"
            except:
                return "Error fetching price"

    return None

# 🔥 Tool: FAQ responder
def faq_tool(user_input):
    user_input_lower = user_input.lower()
    for faq in faqs:
        if faq["question"] in user_input_lower:
            return faq["answer"]
    return None

# API endpoint for website chat
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")

    # 🔥 TOOL FIRST
    tool_result = binance_tool(user_input)
    if tool_result:
        messages.append({"role": "system", "content": tool_result})
        reply = tool_result
    else:
        faq_result = faq_tool(user_input)
        if faq_result:
            messages.append({"role": "system", "content": faq_result})
            reply = faq_result
        else:
            # Default response if nothing matches
            reply = "I will connect you to customer support."

        messages.append({"role": "user", "content": user_input})

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)