'''This module handles the project generation, storage and
retrieval operations'''

import sqlite3
import json
import os
import markdown
from datetime import datetime
from models.database import get_db_connection

def save_project(user_id, skill_level, tech_stack, project_type, content):
    '''Saves project generated to the database and returns the project id'''
    conn = get_db_connection()
    cursor = conn.cursor()

    title = extract_title_from_content(content)

    cursor.execute('''
    INSERT INTO projects (user_id, skill_level, tech_stack, project_type, title, content)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, skill_level, tech_stack, project_type, title, content))

    project_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return project_id


def get_project(project_id):
    '''Retrieve a project by its ID and return project details'''
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id))
    project_row = cursor.fetchone()

    conn.close()

    if project_row:
        project = dict(project_row)

        if project['content']:
            project['html_content'] = markdown.markdown(
                project['content'],
                extensions=['fenced_code', 'cdehilite']
            )
        return project
    return None


def get_user_projects(user_id, limit=10, offset=0):
    '''Get all the user's projects'''
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, skill_level, tech_stack, project_type, cretaed_timestamp
    FROM projects
    WHERE user_id = ?
    ORDER BY created_timestamp DESC
    LIMIT ? OFFSET ?
    ''', (user_id, limit, offset))

    projects = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return projects


def delete_project(project_id, user_id):
    '''Delete project if it belongs to the user and return if deletion was successful'''
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    DELETE FROM projects
    WHERE id = ? and user_id = ?
    ''', (project_id, user_id))

    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return deleted

def update_project(project_id, user_id, updates):
    '''Updates speciic field of a project'''

    allowed_fields = ['title', 'tech_stack', 'content']
    update_fields = {k: v for k, v in updates.items() if k in allowed_fields}

    if not update_fields:
        return False

    set_clause = ', '.join([f"{field} = ?" for field in update_fields])
    values = list(update_fields.values())
    values.extend([project_id, user_id]) 

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(f'''
    UPDATE projects
    SET {set_clause}
    WHERE id = ? AND user_id = ?
    ''', values)

    updated = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return updated


def search_projects(user_id, query, skill_level=None, project_type=None):
    '''Searches for projects based on criterias and return a list of matching projects'''

    conn = get_db_connection()
    cursor = conn.cursor()

    conditions = ['user_id = ?']
    params = [user_id]

    if query:
        conditions.append('(title LIKE ? OR content LIKE ?)')
        search_term = f'%{query}%'
        params.extend([search_term, search_term])

    if skill_level:
        conditions.append('skill_level = ?')
        params.append(skill_level)

    if project_type:
        conditions.append('project_type = ?')
        params.append(project_type)

    where_clause = ' AND '.join(conditions)

    cursor.execute(f'''
    SELECT id, title, skill_level, tech_stack, project_type, created_timestamp
    FROM projects
    WHERE {where_clause}
    ORDER BY created_timestamp DESC
    ''', params)

    projects = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return projects

def get_project_count(user_id=None):
    '''Get count of projects'''
    conn = get_db_connection()
    cursor = conn.cursor()

    if user_id:
        cursor.execute('SELECT COUNT(*) FROM projects WHERE user_id = ?', (user_id))
    else:
        cursor.execute('SELECT COUNT(*) FROM projects')

    count = cursor.fetchone()[0]
    conn.close()

    return count

def extract_title_from_content(content):
    """
    Extract a title from the markdown content.
    Assumes the first line contains a heading.
    
    Args:
        content (str): Markdown content
        
    Returns:
        str: Extracted title or default title
    """
    if not content:
        return "Untitled Project"
    
    # Get the first line and remove markdown heading symbols
    lines = content.strip().split('\n')
    first_line = lines[0].strip()
    
    # Remove markdown heading markers (# symbols)
    if first_line.startswith('#'):
        title = first_line.lstrip('#').strip()
        return title if title else "Untitled Project"
    
    # If no heading found, use first line or default
    return first_line[:50] if first_line else "Untitled Project"

def export_project(project_id, format='json'):
    """
    Export a project in various formats.
    
    Args:
        project_id (int): The ID of the project to export
        format (str): Export format ('json', 'md', 'html')
        
    Returns:
        tuple: (content, mime_type) or (None, None) if error
    """
    project = get_project(project_id)
    
    if not project:
        return None, None
    
    if format == 'json':
        content = json.dumps(project, indent=2)
        mime_type = 'application/json'
    elif format == 'md':
        content = project['content']
        mime_type = 'text/markdown'
    elif format == 'html':
        content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{project['title']}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        pre {{ background: #f4f4f4; border: 1px solid #ddd; border-radius: 4px; padding: 10px; overflow: auto; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>{project['title']}</h1>
    <p><strong>Skill Level:</strong> {project['skill_level']}</p>
    <p><strong>Tech Stack:</strong> {project['tech_stack']}</p>
    <p><strong>Project Type:</strong> {project['project_type']}</p>
    <hr>
    {project['html_content']}
</body>
</html>"""
        mime_type = 'text/html'
    else:
        return None, None
    
    return content, mime_type

def generate_sample_projects():
    """
    Generate sample projects for new users or testing.
    Should be called during initial setup.
    """
    sample_projects = [
        {
            'user_id': 'sample',
            'skill_level': 'beginner',
            'tech_stack': 'HTML, CSS, JavaScript',
            'project_type': 'web',
            'title': 'Interactive Landing Page',
            'content': """# Interactive Landing Page

## Project Overview
Create a responsive landing page with interactive elements using HTML, CSS, and JavaScript.

## Features to Implement
- Hero section with animated background
- Interactive navigation menu
- Product showcase with hover effects
- Contact form with validation
- Responsive design for mobile and desktop

## Learning Objectives
- DOM manipulation
- CSS animations and transitions
- Form validation with JavaScript
- Responsive design principles

## Starter Code
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Landing Page</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Hero Section -->
    <header class="hero">
        <div class="hero-content">
            <h1>Your Product Name</h1>
            <p>A brief description of your amazing product</p>
            <button class="cta-button">Get Started</button>
        </div>
    </header>
    
    <!-- Add more sections here -->
    
    <script src="script.js"></script>
</body>
</html>
```

## Step-by-Step Guide
1. Start by designing the layout
2. Implement the HTML structure
3. Style with CSS, focusing on responsive design
4. Add JavaScript for interactivity
5. Test on different screen sizes

## Resources
- MDN Web Docs for HTML/CSS/JS references
- Google Fonts for typography
- Unsplash for free images
"""
        },
        {
            'user_id': 'sample',
            'skill_level': 'intermediate',
            'tech_stack': 'JavaScript, Flask, SQLite',
            'project_type': 'web',
            'title': 'Task Management Application',
            'content': """# Task Management Application

## Project Overview
Build a task management application with a Flask backend, SQLite database, and JavaScript frontend.

## Core Requirements
- User authentication (login/register)
- Create, read, update, delete tasks
- Categorize tasks and set priorities
- Backend API with Flask
- Frontend interface with JavaScript

## Backend Structure
The backend should provide RESTful endpoints:
- GET /api/tasks - List all tasks
- POST /api/tasks - Create a new task
- PUT /api/tasks/:id - Update a task
- DELETE /api/tasks/:id - Delete a task

## Database Schema
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    priority INTEGER DEFAULT 1,
    category TEXT,
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## Implementation Suggestions
- Use Flask-Login for authentication
- Implement proper error handling in the API
- Create a responsive frontend with vanilla JS or a small framework
- Add sorting and filtering capabilities

## Next Steps
Once the basic application is working, consider adding:
- Task sharing between users
- Email notifications for due dates
- Data visualization for task completion
"""
        },
        {
            'user_id': 'sample',
            'skill_level': 'advanced',
            'tech_stack': 'JavaScript, Python, SQLite',
            'project_type': 'tool',
            'title': 'Code Review Assistant',
            'content': """# Code Review Assistant

## Project Overview
Create a tool that helps developers perform automated code reviews using static analysis and AI assistance.

## Architecture
- Backend: Flask API server
- Frontend: JavaScript SPA
- Database: SQLite for storing projects and review comments
- Integration: GitHub API for repository access

## Key Components

### Static Analysis Engine
Implement a system that can:
- Parse code in multiple languages
- Detect common code smells and anti-patterns
- Check for style guideline violations
- Identify potential performance issues

### AI Integration
Connect with a language model API to:
- Generate natural language explanations of issues
- Suggest code improvements
- Provide contextual documentation references

### Version Control Integration
- Clone repositories from GitHub
- Compare changes between commits
- Comment directly on pull requests

## Technical Challenges
- Creating efficient parsers for multiple languages
- Developing heuristics for code quality assessment
- Handling large repositories efficiently
- Designing an intuitive UI for code review feedback

## Implementation Strategy
1. Start with a focused scope (1-2 programming languages)
2. Build the core static analysis engine
3. Implement the API layer and database
4. Develop the frontend interface
5. Add GitHub integration
6. Incorporate AI assistance features

This project requires strong knowledge of language parsing, software design principles, and API integration.
"""
        }
    ]
    
    # Add samples to database
    for sample in sample_projects:
        save_project(
            sample['user_id'],
            sample['skill_level'],
            sample['tech_stack'],
            sample['project_type'],
            sample['content']
        )