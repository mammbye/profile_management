# Profile Management Microservice

This microservice manages user profiles. It provides endpoints to create, authenticate, retrieve, and delete user accounts.

## API Endpoints (Communication Contract)

- `GET /health`
  - Purpose: Health check
  - Request: none
  - Response (200): `{"status": "healthy", "service": "profile_management"}`

- `POST /users/create`
  - Purpose: Create a new user account
  - Request JSON: `{"username": "string", "password": "string"}`
    - `username`: must be unique
    - `password`: minimum 6 characters (service validates)
  - Success Response (200):
    ```json
    {"user_id": "<uuid>", "username": "<username>", "created_at": "<timestamp>"}
    ```
  - Error Responses:
    - 400: `{"detail": "Username already exists"}`
    - 400: `{"detail": "Password must be at least 6 characters long"}`

- `POST /users/login`
  - Purpose: Authenticate a user
  - Request JSON: `{"username": "string", "password": "string"}`
  - Success Response (200):
    ```json
    {"message": "Login successful", "user_id": "<uuid>", "username": "<username>"}
    ```
  - Error Responses:
    - 401: `{"detail": "Invalid password"}`
    - 404: `{"detail": "User not found"}`

- `GET /users/{user_id}`
  - Purpose: Retrieve a user by UUID
  - Request: path param `user_id`
  - Success Response (200):
    ```json
    {"user_id": "<uuid>", "username": "<username>", "created_at": "<timestamp>"}
    ```
  - Error Response: 404 if not found

- `GET /users/username/{username}`
  - Purpose: Retrieve a user by username
  - Request: path param `username`
  - Success Response (200): same as `GET /users/{user_id}`
  - Error Response: 404 if not found

- `POST /users/delete`
  - Purpose: Delete a user account
  - Request JSON: `{"username": "string", "user_id": "<uuid>"}`
    - The service expects both values and will attempt to delete the profile matching the given `user_id`.
  - Success Response (200):
    ```json
    {"message": "Deleted account for user <username>", "username": "<username>"}
    ```
  - Error Responses:
    - 401: `{"detail": "Invalid user_info"}` (when IDs mismatch)
    - 404: `{"detail": "User not found"}`

## How to programmatically REQUEST data (examples)

Examples using Python `requests` (preferred):

Create user example:

```python
import requests

url = "http://localhost:8000/users/create"
payload = {"username": "newuser@example.com", "password": "securepassword123"}
response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())
# On success: {'user_id': '...', 'username': 'newuser@example.com', 'created_at': '...'}
```

Login example:

```python
import requests

url = "http://localhost:8000/users/login"
payload = {"username": "newuser@example.com", "password": "securepassword123"}
response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())
# On success: {'message': 'Login successful', 'user_id': '...', 'username': '...'}
```

Get user by username example:

```python
import requests

url = "http://localhost:8000/users/username/newuser@example.com"
response = requests.get(url)
print(response.status_code)
print(response.json())
# On success: {'user_id': '...', 'username': 'newuser@example.com', 'created_at': '...'}
```

Delete user example (first fetch user_id via username):

```python
import requests

username = "newuser@example.com"
resp = requests.get(f"http://localhost:8000/users/username/{username}")
if resp.status_code != 200:
    print("User not found")
else:
    user_id = resp.json().get("user_id")
    del_resp = requests.post("http://localhost:8000/users/delete", json={"username": username, "user_id": user_id})
    print(del_resp.status_code)
    print(del_resp.json())
```

## How to programmatically RECEIVE and parse data

The service returns standard JSON responses with HTTP status codes indicating success or failure. Example handling in Python:

```python
# Basic create user response handling
resp = requests.post("http://localhost:8000/users/create", json=payload)
if resp.status_code == 200:
  data = resp.json()
  user_id = data.get("user_id")
  print("Created user_id:", user_id)
else:
  # error payload uses {'detail': '...'}
  error = resp.json().get("detail")
  print("Create failed:", error)


# Login example with specific error handling
login_resp = requests.post("http://localhost:8000/users/login", json={"username": "u", "password": "p"})
if login_resp.status_code == 200:
  login_data = login_resp.json()
  print("Login OK, user_id:", login_data.get("user_id"))
elif login_resp.status_code == 401:
  print("Invalid password")
elif login_resp.status_code == 404:
  print("User not found")
else:
  print("Login error:", login_resp.status_code, login_resp.text)


# Get user by username (handle 404)
g_resp = requests.get("http://localhost:8000/users/username/newuser@example.com")
if g_resp.status_code == 200:
  profile = g_resp.json()
  print("User created at:", profile.get("created_at"))
else:
  print("Get user failed:", g_resp.status_code, g_resp.json().get("detail"))


# Delete user example showing check-then-delete
username = "newuser@example.com"
resp = requests.get(f"http://localhost:8000/users/username/{username}")
if resp.status_code != 200:
  print("Cannot delete - user not found")
else:
  user_id = resp.json().get("user_id")
  del_resp = requests.post("http://localhost:8000/users/delete", json={"username": username, "user_id": user_id})
  if del_resp.status_code == 200:
    print("Deleted:", del_resp.json())
  else:
    print("Delete failed:", del_resp.status_code, del_resp.json().get("detail"))


# Robust request pattern: timeouts, retries (simple), and raise_for_status
from time import sleep
def robust_post(url, json_payload, retries=2, timeout=5):
  for attempt in range(1, retries + 1):
    try:
      r = requests.post(url, json=json_payload, timeout=timeout)
      r.raise_for_status()  # raises on 4xx/5xx
      return r.json()
    except requests.exceptions.HTTPError as he:
      # For client errors, do not retry
      status = getattr(he.response, 'status_code', None)
      if status and 400 <= status < 500:
        raise
      if attempt < retries:
        sleep(0.5)
        continue
      raise
    except requests.exceptions.RequestException:
      if attempt < retries:
        sleep(0.5)
        continue
      raise

try:
  created = robust_post("http://localhost:8000/users/create", {"username": "x", "password": "p"})
  print("Created via robust_post:", created)
except Exception as e:
  print("Robust create failed:", e)
```
### UML Diagram
<img width="434" height="800" alt="image" src="https://github.com/user-attachments/assets/f3f8bc3e-d240-4e85-a456-10092d5b896a" />
