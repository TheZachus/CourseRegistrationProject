import requests
import re

# Login to get a session cookie
def login():
    session = requests.Session()
    
    # must first sign in to login page. must be an admin.
    login_page_url = "http://localhost:8000/login/"
    login_page_response = session.get(login_page_url)
    
    # Search for CSRF token from the response
    csrf_token = None
    if login_page_response.status_code == 200:
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page_response.text)
        if match:
            csrf_token = match.group(1)
    
    if not csrf_token:
        print("Failed to get CSRF token. Authentication will likely fail.")
    
    # login
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

faculty_id = 1  # Default to 1, can be changed as needed

url = f"http://localhost:8000/api/faculty/{faculty_id}/"

response = session.delete(url)

if response.status_code == 204:
    print(f"Faculty with ID {faculty_id} has been successfully deleted.")
elif response.status_code == 404:
    print(f"Faculty with ID {faculty_id} not found.")
else:
    print(f"Failed to delete faculty. Status code: {response.status_code}")
    print(response.text) 