from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not set. Add it in .env or Render Environment Variables.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Serve chatbot frontend
@app.route("/")
def home():
    return render_template("index.html")

# Chat API endpoint
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # OpenAI Chat Completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # cheap + fast, can swap to gpt-4o
            messages=[
                {"role": "system", "content": "You are PlanIt, a helpful career guidance assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200,
            temperature=0.7
        )

        bot_reply = response.choices[0].message.content.strip()
        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    serve(app, host="0.0.0.0", port=port)
