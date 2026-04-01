from dotenv import load_dotenv
import os
import ollama
load_dotenv()
API_KEY=os.getenv("TWELVE_API_KEY")

messages = []

faqs =  [
                {"question": "what are your hours", "answer": "We are open from 9 AM to 6 PM."},
                {"question": "where are you located", "answer": "We are located in Addis Ababa."},
                {"question": "how can i contact you", "answer": "Email us at support@example.com."},
                {"question": "what services do you offer", "answer": "We offer a variety of services including web development, digital marketing, and graphic design."},
                {"question": "do you have any discounts", "answer": "Yes, we offer seasonal discounts. Please check our website for the latest offers."},
                {"question": "what is your return policy", "answer": "Our return policy allows for returns within 30 days of purchase with a valid receipt."},
                {"question": "do you offer international shipping", "answer": "Yes, we offer international shipping. Shipping fees and delivery times vary based on location."},]
   

import requests

def faq_tool(user_input):
    user_input = user_input.lower()
    for faq in faqs:
        if faq['question'] in user_input:
            return faq['answer']
    return None


def ask_ollama_with_memory(user_input):
    
    prompt = """You are a strict customer support assistant.
            TASK : 1 SELECT BEST MATCHING QUESTION TO USER INPUT FROM THE FAQS AND REPLY THE ANSWER OF THE QUESTION.  
                   2 DO NOT EXPLAIN
                   3 DO NOT ANSWER ANYTHING ELSE  
        """

    # add all FAQs
    for faq in faqs:
        prompt += f"Q: {faq['question']}\nA: {faq['answer']}\n\n"

    # add user question ONCE
    prompt += f"User: {user_input}\nAnswer:"

    response = ollama.generate(
        model="tinyllama",
        prompt=prompt
    )

    reply = response['response'].strip()
    reply = reply.split("\n")[0]  # ✅ keep it clean

    if "FAQ" in reply or len(reply) < 5:
        return "I will connect you to support."

    return reply


def chat():
    print("🤖 Customer Support — type 'exit' to quit\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("AI: Goodbye!")
            break

        # 🔥 TOOL FIRST
        tool_result = faq_tool(user_input)

        if tool_result:
            reply =tool_result
        else:
            reply = ask_ollama_with_memory(user_input)

        print("AI:", reply)


chat()