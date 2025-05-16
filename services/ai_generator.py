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
        
    }