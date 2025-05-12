from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    user_prompt = data.get("prompt", "")

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mixtral-8x7b-32768",
            "messages": [
                {
                    "role": "user",
                    "content": f"Suggest a cr4ative coding project for this prompt: {user_prompt}. Include: project title, difficulty, tech stack, short description, and steps to build it."
                }
            ]
        }
    )

    result = response.json()
    idea_text = result['choices'][0]['message']['content']
    return jsonify({"idea": idea_text})

if __name__ == "__main__": 
    app.run(debug=True)
