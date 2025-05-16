from flask import Flask, render_template, request, redirect, url_for, session
from models.database import init_db
from services.ai_generator import generate_project
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

@app.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        skill_level = request.form.get('skill_level')
        tech_stack = request.form.get("tech_stack")
        project_type = request.form.get("project_type")

        project_content = generate_project(skill_level, tech_stack, project_type)
    
if __name__ == "__main__":
    app.run(debug=True)