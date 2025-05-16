from flask import Flask, render_template, request, redirect, url_for, session
from models.database import init_db
from services.ai_generator import generate project
from services.project_service import save_project, get_user_projects
import os

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.before_request
def setup():
    init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=['GET', 'POST'])
def generate():
    data = request.json
    user_prompt = data.get("prompt", "")

    if not user_prompt.strip():
        return jsonify({"error": "Prompt cannot be empty"}), 400
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mixtral-87xb-32768",
        "messages": [
            {"role": "system", "content": "You are an assistant that suggest coding project ideas and help beginners create them."},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": "Failed to get repsonse form API", "details": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)