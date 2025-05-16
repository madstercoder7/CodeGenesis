'''This module handles the API interaction to generate the project ideas
based on user data'''

import os
import json
import markdown
import requests
from dotenv import load_dotenv
from flask import current_app

#Load environment variables
load_dotenv()

#Groq API configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama2-70b-4096" #Alt: "mixtral-8x7b-32768

class GroqAPIError(Exception):
    #Exception for Groq API errors
    pass

def generate_project(skill_level, tech_stack, project_type):
    '''Generates a coding project using Groq API
    Considers the user's skill level, tech stack preferences and project type
    Returns a dictionary of project data for the user'''
    try:
        #Check if API key is available
        if not GROQ_API_KEY:
            current_app.logger.warning("No Groq API key found. Using fallback template")
            return get_fallback_template(skill_level, tech_stack, project_type)
        
        #Create the prompt based on user data
        prompt = create_project_prompt(skill_level, tech_stack, project_type)

        #Call Groq API
        response = call_groq_api(prompt)

        #Process and format the reponse
        project_data = process_api_response(response, skill_level, tech_stack, project_type)

        return project_data
    
    except Exception as e:
        current_app.logger.error(f"Error generating project: {str(e)}")
        #Fallback to template based generation
        return get_fallback_template(skill_level, tech_stack, project_type)


def get_fallback_template():
    '''Creates a prompt for the AI based on user data 
    Returns a formatted prompt for the AI '''

    # System prompt for guiding AI behaviour
    system_prompt = """You are Cynoz, an AI specialized in generating personalized coding projects. 
    Your task is to create practical, education project ideas tailored to user's skill level and interstes.
    Structure your repsonses in markdown format with clear sections and code examples where appropriate.
    Be specific with project requirements and implementation details."""

    # Customize guidance based on skill level
    if skill_level == "beginner":
        guidance = """
        - Project should be achievabel in 1-2 days
        - Include detailed step-by-step instructions
        - Provide complete starter code for critical components
        - Explain code concepts at a basic level
        - Suggest learning resources for unfamiliar concepts
        - Break down the project into small, managebale tasks
        - Focus on fundamental rather than advanced patterns
    """
    
    elif skill_level == "intermediate":
        guidance = """
        - Project should be achievable in 3-7 days
        - Provide project structure and architecture guidance
        - Include starter code for only complex sections
        - Assume familiarity with basic programming concepts
        - Focus on best practices and intermediate patterns
        - Suggest ways to extend the project for additional learning
    """
    else: # advanced
        guidance = """
        - Project should be challenging and take 1-3 weeks
        - Focus on high-level architecture and technical decisions
        - Minimal code exmaples (pseudocode or skeleton only)
        - Introduce advanced concepts and design patterns
        - Emphasize scalability, performance and code quality
        - Suggest areas for creative probelm-solving
    """
        
    # Create the user prompt
    user_prompt = f"""
    Genrate a coding project for a {skill_level} developer with the following criteria:
    Tech Stack: {tech_stack}
    Project type: {project_type}

    Requirements:
    {guidance}

    Format your response with the following sections:
    1. Project title (a creative, descriptive name)
    2. Overview (brief description of the project)
    3. Learning Objectives (what skills be practiced)
    4. Features (what the project shoudl accomplish)
    5. Implementation details (architecture, components, etc.)
    6. Getting started (setup instructions)
    7. Development steps (breakdown of implementation tasks)
    8. Code examples (key components with explanations)
    9. Testing (how to verify functionality)
    10. Resources (helpful documentation, tutorials)
    11. Extensions (optional ways to enhance the project)

    Make sure ALL the code examples are syntactically correct and properly formatted for the specified tech stack.
    """

    return {
        "system": system_prompt,
        "user": user_prompt
    }


def call_groq_api(prompt):
    '''Calling the Groq API with the system and user prompt
    Returns generated API content
    Raises error if API call fails'''
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": prompt["system"]},
            {"role": "system", "content": prompt["user"]}
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            raise GroqAPIError(f"API returned status code {response.status_code}: {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        raise GroqAPIError(f"Request to Groq API failed: {str(e)}")
    

def process_api_response(response_text, skill_level, tech_stack, project_type):
    # Process and format the API response using the data returned from the API call

    # Extract title from the repsonse
    lines = response_text.strip().split('\n')
    title = "New Coding Project"

    for line in lines:
        if line.startswith('# '):
            title = line.replace('# ', '').strip()
            break

    # Covert markdown to HTML for display
    html_content = markdown.markdown(response_text, extensions=['fenced_code', 'tables'])

    project_data = {
        "title": title,
        "skill_level": skill_level,
        "tech_stack": tech_stack,
        "project_type": project_type,
        "content_markdown": response_text,
        "content_html": html_content
    }

    return project_data


def get_fallback_template(skill_level, tech_stack, project_type):
    '''Provide a pre-written project template if the API fails'''

    templates = {
        "beginner_web": {
            "title": "Personal Portfolio Website",
            "content_markdown": """# Personal Portfolio Website

            ## Overview
            Create a personal portfolio website to showcase your projects and skills.

            ## Learning Objectives
            - HTML structure and semantic elements
            - CSS styling and responsive design
            - Basic JavaScript for interactivity

            ## Features
            - Home page with introduction
            - Projects section
            - Skills section
            - Contact form

            ## Implementation Details
            Create a multi-page or single-page website with clean, responsive design.

            ## Getting Started
            1. Set up your project folder
            2. Create HTML files for each page or section
            3. Create CSS files for styling
            4. Add JavaScript for interactive elements

            ## Code Examples

            ### HTML Structure
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>My Portfolio</title>
                <link rel="stylesheet" href="styles.css">
            </head>
            <body>
                <header>
                    <nav>
                        <ul>
                            <li><a href="#home">Home</a></li>
                            <li><a href="#projects">Projects</a></li>
                            <li><a href="#skills">Skills</a></li>
                            <li><a href="#contact">Contact</a></li>
                        </ul>
                    </nav>
                </header>
                
                <main>
                    <section id="home">
                        <h1>Hi, I'm [Your Name]</h1>
                        <p>I'm a web developer passionate about creating amazing websites.</p>
                    </section>
                    
                    <!-- Other sections go here -->
                </main>
                
                <footer>
                    <p>&copy; 2025 [Your Name]</p>
                </footer>
                
                <script src="script.js"></script>
            </body>
            </html>
            ```

            ### CSS Example
            ```css
            /* Base styles */
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
            }

            header {
                background-color: #333;
                color: white;
                padding: 1rem;
            }

            nav ul {
                display: flex;
                list-style: none;
                padding: 0;
            }

            nav li {
                margin-right: 1rem;
            }

            nav a {
                color: white;
                text-decoration: none;
            }

            section {
                padding: 2rem;
                min-height: 100vh;
            }
            ```

            ### JavaScript Example
            ```javascript
            // Smooth scrolling for navigation links
            document.querySelectorAll('nav a').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    const targetId = this.getAttribute('href');
                    const targetSection = document.querySelector(targetId);
                    
                    window.scrollTo({
                        top: targetSection.offsetTop,
                        behavior: 'smooth'
                    });
                });
            });
            ```

            ## Testing
            - Validate HTML using W3C Validator
            - Test responsive design using browser dev tools
            - Check all links and navigation

            ## Resources
            - MDN Web Docs: https://developer.mozilla.org/
            - CSS-Tricks: https://css-tricks.com/
            - W3Schools: https://www.w3schools.com/

            ## Extensions
            - Add animations with CSS
            - Implement a dark/light mode toggle
            - Create a blog section
            """
                    },
                    
                    
            "intermediate_web": {
                "title": "Weather Dashboard with API Integration",
                "content_markdown": """# Weather Dashboard with API Integration

            ## Overview
            Build an interactive weather dashboard that fetches and displays weather data from a public API.

            ## Learning Objectives
            - Working with external APIs
            - Asynchronous JavaScript (fetch/promises)
            - Dynamic DOM manipulation
            - Data visualization

            ## Features
            - Current weather conditions display
            - 5-day forecast
            - Location search functionality
            - Save favorite locations
            - Visual representation of weather data

            ## Implementation Details
            Use a weather API (like OpenWeatherMap) to fetch weather data based on user location or search. Display the data in an intuitive and visually appealing dashboard.

            ## Getting Started
            1. Sign up for a free API key at OpenWeatherMap
            2. Set up your project structure
            3. Create the UI components
            4. Implement API calls and data processing

            ## Development Steps
            1. Design the dashboard layout
            2. Implement the search functionality
            3. Create API utility functions
            4. Build data visualization components
            5. Add local storage for saving favorites

            ## Code Examples

            ### API Utility Function
            ```javascript
            // weather-api.js
            const API_KEY = 'your_api_key_here';
            const BASE_URL = 'https://api.openweathermap.org/data/2.5';

            async function getWeatherByCity(city) {
                try {
                    const response = await fetch(`${BASE_URL}/weather?q=${city}&units=metric&appid=${API_KEY}`);
                    
                    if (!response.ok) {
                        throw new Error(`Weather data not found (${response.status})`);
                    }
                    
                    return await response.json();
                } catch (error) {
                    console.error('Error fetching weather data:', error);
                    throw error;
                }
            }

            async function getForecast(lat, lon) {
                try {
                    const response = await fetch(
                        `${BASE_URL}/forecast?lat=${lat}&lon=${lon}&units=metric&appid=${API_KEY}`
                    );
                    
                    if (!response.ok) {
                        throw new Error(`Forecast data not found (${response.status})`);
                    }
                    
                    return await response.json();
                } catch (error) {
                    console.error('Error fetching forecast data:', error);
                    throw error;
                }
            }

            export { getWeatherByCity, getForecast };
            ```

            ### Main App Logic
            ```javascript
            // app.js
            import { getWeatherByCity, getForecast } from './weather-api.js';

            // DOM Elements
            const searchForm = document.getElementById('search-form');
            const cityInput = document.getElementById('city-input');
            const currentWeatherEl = document.getElementById('current-weather');
            const forecastEl = document.getElementById('forecast');
            const favoritesEl = document.getElementById('favorites');

            // Load favorites from localStorage
            const favorites = JSON.parse(localStorage.getItem('favorites')) || [];

            // Initialize the app
            function init() {
                renderFavorites();
                
                // Load weather for default city or first favorite
                const defaultCity = favorites[0] || 'New York';
                loadWeatherData(defaultCity);
                
                // Set up event listeners
                searchForm.addEventListener('submit', handleSearch);
            }

            async function handleSearch(e) {
                e.preventDefault();
                const city = cityInput.value.trim();
                
                if (city) {
                    await loadWeatherData(city);
                    cityInput.value = '';
                }
            }

            async function loadWeatherData(city) {
                try {
                    // Show loading state
                    currentWeatherEl.innerHTML = '<p>Loading...</p>';
                    forecastEl.innerHTML = '';
                    
                    // Get current weather
                    const weatherData = await getWeatherByCity(city);
                    
                    // Use coordinates to get forecast
                    const { lat, lon } = weatherData.coord;
                    const forecastData = await getForecast(lat, lon);
                    
                    // Render the data
                    renderCurrentWeather(weatherData);
                    renderForecast(forecastData);
                } catch (error) {
                    currentWeatherEl.innerHTML = `<p class="error">Error: ${error.message}</p>`;
                }
            }

            // Render functions and other app logic would follow...

            init();
            ```

            ## Testing
            - Test with different city inputs
            - Verify API error handling
            - Test responsiveness on different devices
            - Check local storage functionality

            ## Resources
            - OpenWeatherMap API: https://openweathermap.org/api
            - MDN Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
            - Chart.js (for data visualization): https://www.chartjs.org/

            ## Extensions
            - Add weather maps
            - Implement geolocation for current position
            - Add weather alerts
            - Create hourly forecast view
            """
        },


        "advanced_web": {
            "title": "Real-time Collaborative Task Management System",
            "content_markdown": """# Real-time Collaborative Task Management System

            ## Overview
            Build a collaborative task management application with real-time updates, allowing teams to organize projects and tasks with live synchronization across clients.

            ## Learning Objectives
            - Real-time communication with WebSockets
            - Advanced state management
            - Database design and optimization
            - Authentication and authorization
            - Front-end/back-end architecture

            ## Features
            - User authentication and team management
            - Project and task creation with hierarchical organization
            - Real-time updates when tasks change
            - File attachments and comments
            - Notifications and activity feed
            - Filtering and advanced search

            ## Implementation Details
            Create a Flask backend API with SQLite database and incorporate WebSockets for real-time updates. Build a dynamic front-end using vanilla JavaScript with proper state management patterns.

            ## Architecture Overview

            ### Backend
            - Flask application serving REST API endpoints
            - WebSockets for real-time communication
            - SQLite database with appropriate indexes
            - Authentication middleware
            - File storage system

            ### Frontend
            - Component-based architecture
            - State management system
            - WebSocket client integration
            - Responsive design system
            - Offline capabilities using localStorage

            ## Getting Started
            1. Set up your development environment
            2. Design your database schema
            3. Create API endpoints
            4. Implement WebSocket handlers
            5. Build frontend components

            ## Development Steps
            1. Create database models and relationships
            2. Implement user authentication system
            3. Build REST API endpoints for CRUD operations
            4. Set up WebSocket server for real-time events
            5. Develop frontend state management
            6. Implement UI components with real-time bindings

            ## Code Examples

            ### WebSocket Server Setup
            ```python
            # websocket_server.py
            from flask import Flask
            from flask_socketio import SocketIO, emit, join_room, leave_room
            from flask_jwt_extended import jwt_required, get_jwt_identity

            app = Flask(__name__)
            socketio = SocketIO(app, cors_allowed_origins="*")

            # Connected clients by user_id
            connected_users = {}

            @socketio.on('connect')
            def handle_connect():
                print('Client connected')

            @socketio.on('authenticate')
            def handle_authenticate(data):
                try:
                    # Verify JWT token (simplified - implement proper validation)
                    user_id = verify_token(data['token'])
                    if not user_id:
                        return False
                    
                    # Associate socket with user
                    connected_users[user_id] = request.sid
                    
                    # Join user to their personal room
                    join_room(f"user_{user_id}")
                    
                    # Join all project rooms the user is a member of
                    projects = get_user_projects(user_id)
                    for project in projects:
                        join_room(f"project_{project.id}")
                        
                    emit('authenticated', {'status': 'success'})
                except Exception as e:
                    print(f"Authentication error: {str(e)}")
                    return False

            @socketio.on('task_update')
            def handle_task_update(data):
                try:
                    # Verify user has permission to update this task
                    user_id = get_user_from_socket(request.sid)
                    task_id = data['task_id']
                    
                    if not user_can_edit_task(user_id, task_id):
                        return
                    
                    # Update task in database
                    update_task(task_id, data['updates'])
                    
                    # Get the project_id for this task
                    project_id = get_project_id_for_task(task_id)
                    
                    # Broadcast to all users in this project room
                    emit('task_changed', {
                        'task_id': task_id,
                        'updates': data['updates'],
                        'updated_by': user_id,
                        'timestamp': current_timestamp()
                    }, room=f"project_{project_id}")
                    
                except Exception as e:
                    print(f"Task update error: {str(e)}")

            @socketio.on('disconnect')
            def handle_disconnect():
                # Remove user from connected_users
                for user_id, sid in connected_users.items():
                    if sid == request.sid:
                        del connected_users[user_id]
                        break
                print('Client disconnected')

            if __name__ == '__main__':
                socketio.run(app, debug=True)
            ```

            ### Frontend WebSocket Integration
            ```javascript
            // websocket-client.js
            class TaskSocket {
                constructor(baseUrl, authToken) {
                    this.socket = null;
                    this.baseUrl = baseUrl;
                    this.authToken = authToken;
                    this.connectionPromise = null;
                    this.eventHandlers = {
                        'task_changed': [],
                        'project_updated': [],
                        'comment_added': []
                    };
                }
                
                connect() {
                    if (this.connectionPromise) {
                        return this.connectionPromise;
                    }
                    
                    this.connectionPromise = new Promise((resolve, reject) => {
                        this.socket = io(this.baseUrl);
                        
                        this.socket.on('connect', () => {
                            console.log('Socket connected');
                            
                            // Authenticate with the server
                            this.socket.emit('authenticate', { token: this.authToken });
                        });
                        
                        this.socket.on('authenticated', () => {
                            console.log('Socket authenticated');
                            resolve(this.socket);
                        });
                        
                        this.socket.on('authentication_failed', (error) => {
                            console.error('Socket authentication failed:', error);
                            reject(error);
                        });
                        
                        this.socket.on('disconnect', () => {
                            console.log('Socket disconnected');
                            this.connectionPromise = null;
                        });
                        
                        // Set up event listeners
                        this.socket.on('task_changed', (data) => {
                            this._triggerEvent('task_changed', data);
                        });
                        
                        this.socket.on('project_updated', (data) => {
                            this._triggerEvent('project_updated', data);
                        });
                        
                        this.socket.on('comment_added', (data) => {
                            this._triggerEvent('comment_added', data);
                        });
                    });
                    
                    return this.connectionPromise;
                }
                
                on(event, callback) {
                    if (!this.eventHandlers[event]) {
                        this.eventHandlers[event] = [];
                    }
                    
                    this.eventHandlers[event].push(callback);
                    return this;
                }
                
                _triggerEvent(event, data) {
                    if (this.eventHandlers[event]) {
                        this.eventHandlers[event].forEach(callback => callback(data));
                    }
                }
                
                updateTask(taskId, updates) {
                    this.connect().then(() => {
                        this.socket.emit('task_update', {
                            task_id: taskId,
                            updates: updates
                        });
                    });
                }
                
                disconnect() {
                    if (this.socket) {
                        this.socket.disconnect();
                        this.socket = null;
                        this.connectionPromise = null;
                    }
                }
            }

            export default TaskSocket;
            ```

            ## Database Schema
            ```sql
            -- Users table
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Projects table
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            );

            -- Project members
            CREATE TABLE project_members (
                project_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,  -- 'owner', 'editor', 'viewer'
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (project_id, user_id),
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            -- Tasks table
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                priority INTEGER NOT NULL,
                assigned_to INTEGER,
                created_by INTEGER NOT NULL,
                parent_task_id INTEGER,
                due_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (assigned_to) REFERENCES users (id),
                FOREIGN KEY (created_by) REFERENCES users (id),
                FOREIGN KEY (parent_task_id) REFERENCES tasks (id)
            );

            -- Task comments
            CREATE TABLE comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            -- Task attachments
            CREATE TABLE attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                uploaded_by INTEGER NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (uploaded_by) REFERENCES users (id)
            );

            -- Activity logs
            CREATE TABLE activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,  -- 'task', 'project', 'comment'
                entity_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );

            -- Create indexes for performance
            CREATE INDEX idx_tasks_project_id ON tasks (project_id);
            CREATE INDEX idx_tasks_assigned_to ON tasks (assigned_to);
            CREATE INDEX idx_comments_task_id ON comments (task_id);
            CREATE INDEX idx_attachments_task_id ON attachments (task_id);
            CREATE INDEX idx_activity_logs_entity ON activity_logs (entity_type, entity_id);
            ```

            ## Testing
            - Unit test API endpoints
            - Integration tests for WebSocket functionality
            - End-to-end testing with automated UI tests
            - Load testing for concurrent users

            ## Resources
            - Flask-SocketIO: https://flask-socketio.readthedocs.io/
            - WebSockets API: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
            - SQLite Documentation: https://www.sqlite.org/docs.html

            ## Extensions
            - Implement data synchronization for offline mode
            - Add keyboard shortcuts for power users
            - Create a mobile app version using the same backend
            - Add time tracking features
            - Implement advanced analytics dashboard
            """
        }
    }

    key = f"{skill_level}_{project_type}"
    if key in templates:
        template = templates[key]
    else:
        template = templates["beginner_web"]
        template["title"] = f"New {project_type.capitalize()} Project with {tech_stack}"

    html_content = markdown.markdown(template["content_markdown"], extensions=['fenced_code', 'tables'])

    return {
        "title": template["title"],
        "skill_level": skill_level,
        "tech_stack": tech_stack,
        "project_type": project_type,
        "content_markdown": template["content_markdown"],
        "content_html": html_content
    }