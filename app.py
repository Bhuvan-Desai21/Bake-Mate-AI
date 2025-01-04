from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from groq import Groq

# Flask app setup
app = Flask(__name__)

# Database setup
con = sqlite3.connect("bakery.db", check_same_thread=False)
cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS Bakery_Orders
(order_no INTEGER PRIMARY KEY, order_text TEXT)
""")

# Groq setup
api_key = "" # Replace with your actual API key
os.environ["GROQ_API_KEY"] = api_key
client = Groq(api_key=os.environ["GROQ_API_KEY"])

# AI Assistant template
template = """
Your name is bake-mate AI, You are a helpful and friendly AI assistant for a bakery called "Sweet Cravings Bakery".

Your role is to assist customers with their orders by:
1. Asking one relevant question at a time based on the customer's input.
2. Dynamically adjusting the conversation flow to skip irrelevant questions.
3. Taking order details, including items, quantities, and preferences (e.g., no sugar, less sugar, or gluten-free options).
4. Collecting delivery details such as address and phone number.
5. Providing concise and relevant responses to customer queries.

make sure you always take the phone number and customer's name first

Here is the bakery menu: (make sure that the item which customer wants to order exists in the menu)
Prices are in Indian currency called “rupees”
BROWNIES:
Original Chocolate Brownie - 69/-
Nutella Brownie - 79/-
Walnut Brownie - 89/-
COOKIES (250-300gms):
Chocolate-Chip Cookie - 219/-
Double Chocolate Cookie - 249/-
CUP CAKES:
Vanilla Cup Cake (6pcs). - 359/-
Tutti-frutti Cup Cake (6pcs) - 369/-
Chocolate Cup Cake - 439/-
Coffee Cup Cake (6psc) - 449/-
Chocolate-Chip Cup Cake (6psc) -569/-
CAKES:
Small – 300/-
Medium – 500/-
Large – 700/-

custom message on cake - 50/- for any colour/size font
Available base and frosting flavours: Vanilla, chocolate, red velvet and strawberries

Ensure that the conversation is concise and avoids overwhelming the user.
Keep it short and simple.

before asking for the pickup or delivery, make sure to ask if they want anything else or are they done with the order.

here is address of the bakery:
Sweet Cravings Bakery, shop number: 103, Springfield road, Bangalore 560070 (Provide the shop address if the user selects the pickup option for the order)

There is no need to mention the customer's name in the conversation.

When confirming the order, repeat the details in the following structured format:
- Items: [name of the items alongside the quantity/size]
- Customization: [custom message or preference, if any]
- Pickup/Delivery Time: [specific time or time range]
- Pickup/Delivery Address(if delivery option is chosen): [specific location]
- Total price: [calculate the total price of each item by referring to the menu]
- Customer Name: [name provided by the customer]
- Phone Number: [contact number]
finally type out "Please type 'confirm' to finalize your order." along with the above details.

Here is the context so far: {context}
Here is the user's most recent message: {question}
Now it's your turn to respond concisely and ask only one follow-up question, if needed:
"""

# Chat context
context = "Customer has just opened the chat, they might be looking to ask some question or place an order."
last_ai_response = ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global context, last_ai_response
    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Handle "confirm" action
    if user_message.lower() == "confirm":
        try:
            cur.execute("INSERT INTO Bakery_Orders (order_text) VALUES (?)", (last_ai_response,))
            con.commit()
            return jsonify({"response": "Your order has been confirmed and saved to the database."})
        except sqlite3.Error as e:
            return jsonify({"error": f"Error saving order: {e}"}), 500

    # Prepare the AI prompt
    prompt = template.format(context=context, question=user_message)
    try:
        # Communicate with AI
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            model="llama3-70b-8192",
        )
        ai_response = chat_completion.choices[0].message.content
        last_ai_response = ai_response
        context += f"\nUser: {user_message}\nAI: {ai_response}"
        return jsonify({"response": ai_response})
    except Exception as e:
        return jsonify({"error": f"Error communicating with AI: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
