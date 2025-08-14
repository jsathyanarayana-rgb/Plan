from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load Hugging Face token from .env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # Allow HTML/JS to talk to Flask

API_URL = "https://api-inference.huggingface.co/models/openai/gpt-oss-20b:fireworks-ai"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# Serve the chatbot HTML
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

        # Send to Hugging Face API
        payload = {
            "inputs": f"User: {user_message}\nAI:",
            "parameters": {"max_new_tokens": 200, "temperature": 0.7}
        }
        response = requests.post(API_URL, headers=HEADERS, json=payload)

        if response.status_code != 200:
            return jsonify({
                "error": f"HF API error {response.status_code}",
                "details": response.text
            }), 500

        data = response.json()
        bot_reply = data[0].get("generated_text", "").replace(
            f"User: {user_message}\nAI:", ""
        ).strip()

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT env var
    serve(app, host="0.0.0.0", port=port)
