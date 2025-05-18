from flask import Flask, render_template, request, redirect, url_for, session
import os
from services.ai_generator import generate_project
from services.project_service import save_project, get_project, get_user_projects
from models.database import init_db

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
        project_id = save_project(session.get('user_id', 'anonymous'),
                                  skill_level, tech_stack, project_content)
        
        return redirect(url_for('view_project', project_id=project_id))
    
    return render_template('generate.html')

@app.route('/project/<int:project_id>')
def view_project(project_id):
    project = get_project(project_id)
    return render_template('project.html', project=project)

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id', 'anonymous')
    projects = get_user_projects(user_id)
    return render_template('dashboard.html', projects=projects)
    
if __name__ == "__main__":
    app.run(debug=True)