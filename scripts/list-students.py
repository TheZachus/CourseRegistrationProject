import requests
import re

# Login to get a session cookie
def login():
    session = requests.Session()
    
    # must first sign in to login page. must be an admin.
    login_page_url = "http://localhost:8000/login/"
    login_page_response = session.get(login_page_url)
    
    # Get CSRF token from the response
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

# Get session
session = login()
if not session:
    print("Authentication failed. Exiting.")
    exit(1)

url = "http://localhost:8000/api/students/"

response = session.get(url)

if response.status_code == 200:
    students = response.json()
    student_info = [f"Student #{i}: ID={s['id']}, User ID={s['user']}, Address={s['home_address']}, " 
                   f"Phone={s['phone_number']}, Semester={s['current_semester'] or 'None'}" 
                   for i, s in enumerate(students, 1)]
    print(f"Total students: {len(students)}\n" + "\n".join(student_info))
else:
    print(f"Failed to retrieve students. Status code: {response.status_code} - {response.text}") 