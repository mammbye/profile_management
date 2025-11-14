import requests
import json

# Base URL for the profile_management microservice (update if needed)
BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint."""
    print("1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Request: GET {BASE_URL}/health")
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    assert response.status_code == 200
    print("✓ Health check passed\n")


def test_create_user():
    """Test user creation."""
    print("2. Testing user creation...")
    payload = {"username": "testuser4@withemail.com",
               "password": "securepass123"}
    response = requests.post(f"{BASE_URL}/users/create", json=payload)
    print(
        f"Request: POST {BASE_URL}/users/create with payload {json.dumps(payload)}")
    print(f"Response Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response Body: {data}")
        user_id = data.get("user_id")
        print("✓ User created successfully\n")
        return user_id
    else:
        print(f"Response Body: {response.json()}")
        print("✗ User creation failed (expected if username exists)\n")
        return None


def test_user_creation_existing_username():
    """Test user creation with an existing username."""
    print("3. Testing user creation with existing username...")
    payload = {"username": "testuser4@withemail.com",
               "password": "anotherpass123"}
    response = requests.post(f"{BASE_URL}/users/create", json=payload)
    print(
        f"Request: POST {BASE_URL}/users/create with payload {json.dumps(payload)}")
    print(f"Response Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response Body: {data}")
        print("✗ User creation should have failed but succeeded\n")
    else:
        print(f"Response Body: {response.json()}")
        print("✓ Correctly handled existing username\n")


def test_login():
    """Test user login."""
    print("4. Testing user login...")
    payload = {"username": "testuser", "password": "securepass123"}
    response = requests.post(f"{BASE_URL}/users/login", json=payload)
    print(
        f"Request: POST {BASE_URL}/users/login with payload {json.dumps(payload)}")
    print(f"Response Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response Body: {data}")
        print("✓ Login successful\n")
    else:
        print(f"Response Body: {response.json()}")
        print("✗ Login failed\n")


def test_wrong_login():
    """Test user login with wrong password."""
    print("5. Testing user login with wrong password...")
    payload = {"username": "testuser", "password": "wrongpassword"}
    response = requests.post(f"{BASE_URL}/users/login", json=payload)
    print(
        f"Request: POST {BASE_URL}/users/login with payload {json.dumps(payload)}")
    print(f"Response Status: {response.status_code}")
    if response.status_code == 401:
        print(f"Response Body: {response.json()}")
        print("✓ Correctly handled wrong password\n")
    else:
        print(f"Response Body: {response.json()}")
        print("✗ Failed to handle wrong password correctly\n")


def test_get_user_by_username():
    """Test getting user by username."""
    print("6. Testing get user by username...")
    username = "testuser"
    response = requests.get(f"{BASE_URL}/users/username/{username}")
    print(f"Request: GET {BASE_URL}/users/username/{username}")
    print(f"Response Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response Body: {data}")
        print("✓ User retrieved successfully\n")
    else:
        print(f"Response Body: {response.json()}")
        print("✗ User retrieval failed\n")


def test_get_user_by_id(user_id):
    """Test getting user by ID."""
    print("7. Testing get user by ID...")
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    print(f"Request: GET {BASE_URL}/users/{user_id}")
    print(f"Response Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response Body: {data}")
        print("✓ User retrieved successfully\n")
    else:
        print(f"Response Body: {response.json()}")
        print("✗ User retrieval failed\n")


def test_delete_user_by_username(username):
    """Test deleting user by username."""
    print("8. Testing delete user by username...")
    payload = {"username": username}
    response = requests.post(f"{BASE_URL}/users/delete", json=payload)
    print(
        f"Request: POST {BASE_URL}/users/delete with payload {json.dumps(payload)}")
    print(f"Response Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response Body: {data}")
        print("✓ User deleted successfully\n")
    else:
        print(f"Response Body: {response.json()}")
        print("✗ User deletion failed\n")


# Main execution: Call tests in sequence
if __name__ == "__main__":
    print("Starting microservice tests...\n")
    try:
        test_health()
        user_id = test_create_user()
        test_user_creation_existing_username()
        test_login()
        test_wrong_login()
        test_get_user_by_username()
        test_get_user_by_id(user_id)
        test_delete_user_by_username("testuser")

        print("All tests completed.")
    except Exception as e:
        print(f"Test failed with error: {e}")
