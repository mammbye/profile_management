import requests
import json

# Base URL for the profile_management microservice (update if needed)
BASE_URL = "http://localhost:8000"

# Test configuration: edit these values to run the tests with different credentials
CONFIG = {
    "username": "testuser4@withemail.com",
    "password": "securepass123",
    "alt_password": "anotherpass123",
    "wrong_password": "wrongpassword"
}


def test_health():
    """Test health check endpoint."""
    print("1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Request: GET {BASE_URL}/health")
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.json()}")
    assert response.status_code == 200
    print("✓ Health check passed\n")


def test_create_user(username, password):
    """Test user creation."""
    print("2. Testing user creation...")
    payload = {"username": username,
               "password": password}
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


def test_user_creation_existing_username(username, alt_password):
    """Test user creation with an existing username."""
    print("3. Testing user creation with existing username...")
    payload = {"username": username,
               "password": alt_password}
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


def test_login(username, password):
    """Test user login."""
    print("4. Testing user login...")
    payload = {"username": username,
               "password": password}
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


def test_wrong_login(username, wrong_password):
    """Test user login with wrong password."""
    print("5. Testing user login with wrong password...")
    payload = {"username": username,
               "password": wrong_password}
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


def test_get_user_by_username(username):
    """Test getting user by username."""
    print("6. Testing get user by username...")
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
    # First fetch the user's id to ensure we send a matching pair
    resp = requests.get(f"{BASE_URL}/users/username/{username}")
    print(f"Request: GET {BASE_URL}/users/username/{username}")
    print(f"Response Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Response Body: {resp.json()}")
        print("✗ Cannot delete - user not found\n")
        return
    user_data = resp.json()
    user_id = user_data.get("user_id")

    payload = {"username": username, "user_id": user_id}
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
        username = CONFIG["username"]
        password = CONFIG["password"]
        alt_password = CONFIG["alt_password"]
        wrong_password = CONFIG["wrong_password"]
        user_id = test_create_user(username, password)
        # if username already exists, fetch its id
        if not user_id:
            resp = requests.get(f"{BASE_URL}/users/username/{username}")
            if resp.status_code == 200:
                user_id = resp.json().get("user_id")
                print(f"Found existing user_id for {username}: {user_id}\n")
            else:
                print(
                    f"Could not determine user_id for {username}; some tests will be skipped\n")
        test_user_creation_existing_username(username, alt_password)
        test_login(username, password)
        test_wrong_login(username, wrong_password)
        test_get_user_by_username(username)
        test_id = user_id if user_id else "invalid-uuid"
        test_get_user_by_id(test_id)
        test_delete_user_by_username(username)

        print("All tests completed.")
    except Exception as e:
        print(f"Test failed with error: {e}")
