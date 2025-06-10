import requests
import re

# Login to get a session cookie
def login():
    session = requests.Session()
    
    # must first sign in to login page. must be an admin.
    login_page_url = "http://localhost:8000/login/"
    login_page_response = session.get(login_page_url)
    
    # search for CSRF token from the response
    csrf_token = None
    if login_page_response.status_code == 200:
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page_response.text)
        if match:
            csrf_token = match.group(1)
    
    if not csrf_token:
        print("Failed to get CSRF token. Authentication will likely fail.")
    
    # Now login
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

# check authenticated session
session = login()
if not session:
    print("Authentication failed. Exiting.")
    exit(1)

user_id = 1 #can be changed to any user id

url = "http://localhost:8000/api/users/{user_id}/"

get_response = session.get(url)

if get_response.status_code != 200:
    print(f"Failed to retrieve user with ID {user_id}. Status code: {get_response.status_code} - {get_response.text}")

user_data = get_response.json()

response = user_data.put({"first_name": "Updated First Name", "last_name": "Updated Last Name",
    "email": "updated.email@example.com"})

if response.status_code == 200:
    user_data = response.json()
    print(f"Updated User Successfully: {user_data}")
else:
    print(f"Failed to update user. Status code: {response.status_code} - {response.text}")  