import requests
import json
import re

# Login to get a session cookie
def login():
    session = requests.Session()
    
    # must first sign in to login page. must be an admin.
    login_page_url = "http://localhost:8000/login/"
    login_page_response = session.get(login_page_url)
    
    # Get CSRF token from the response
    if login_page_response.status_code == 200:
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page_response.text)
        if match:
            csrf_token = match.group(1)
        else:
            print("Failed to get CSRF token. Authentication will likely fail.")
    
    #login
    login_data = {
        "username": "testadmin",
        "password": "Password-123",
        "csrfmiddlewaretoken": csrf_token
    }
    
    headers = {
        "Referer": login_page_url
    }
    
    response = session.post(login_page_url, data=login_data, headers=headers, allow_redirects=True)
    
    if response.status_code == 200 and "dashboard" in response.url:
        print("Login successful")
        return session
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

# Get session
session = login()
if not session:
    print("Authentication failed. Exiting.")
    exit(1)

url = "http://localhost:8000/api/courses/"

course_data = {
    "course_name": "Introduction to Python",
    "description": "A comprehensive introduction to Python programming language",
    "instructor": 1,  # Replace with an existing faculty ID
    "credits": 3,
    "semester": 1,  # Replace with an existing semester ID
}

response = session.post(url, json=course_data)

if response.status_code == 201:
    print(f"Course created successfully: {json.dumps(response.json(), indent=2)}")
else:
    print(f"Failed to create course. Status code: {response.status_code} - {response.text}") 