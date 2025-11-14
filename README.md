# Profile Management Microservice

## API Endpoints

- `GET /health` - Health check
- `POST /users/create` - Create new user
- `POST /users/login` - User authentication
- `GET /users/{user_id}` - Get user by ID
- `GET /users/username/{username}` - Get user by username
- `Post /users/delete_user/{username}` - Delete user by username

## Usage Examples

### POST Data (Create User)

```bash
curl -X POST http://localhost:8000/users/create \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123", "timezone": "UTC"}'
```

### POST Data (Login)

```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123"}'
```

### GET Data (Get user by username)

```bash
curl http://localhost:8000/users/username/john
```

### POST Data (Delete User)

```bash
curl -X POST http://localhost:8000/users/delete \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "user_id": "<INSERT_YOUR_USER_ID_HERE>"}'
```

## TEST PROGRAM

### Example Request (Create User - POST)

```python
import requests

url = "http://localhost:8000/users/create"
payload = {"username": "newuser@example.com", "password": "securepassword123"}
response = requests.post(url, json=payload)
print(response.status_code)  # Expected: 200 on success
print(response.json())  # Response data
```

### Example Request (Login - POST)

```python
import requests

url = "http://localhost:8000/users/login"
payload = {"username": "newuser@example.com", "password": "securepassword123"}
response = requests.post(url, json=payload)
print(response.status_code)  # Expected: 200 on success
print(response.json())  # Response data with user_id and username
```

### Example Request (Get User by Username - GET)

```python
import requests

url = "http://localhost:8000/users/username/newuser@example.com"
response = requests.get(url)
print(response.status_code)  # Expected: 200 on success
print(response.json())  # Response data with user details
```
