from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import uuid
from typing import Dict
import os
import bcrypt
from datetime import datetime

app = FastAPI(title="Profile Management Microservice")

# Data storage file
PROFILES_FILE = os.path.join(os.path.dirname(__file__), "user_profiles.json")


# Pydantic models
class UserProfile(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user_id: str
    username: str
    created_at: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    user_id: str
    username: str


class DeleteRequest(BaseModel):
    username: str
    user_id: str


class DeleteResponse(BaseModel):
    message: str
    username: str


# Helper functions for JSON storage
def load_profiles() -> Dict[str, dict]:
    """Load user profiles from JSON file"""
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_profiles(profiles: Dict[str, dict]):
    """Save user profiles to JSON file"""
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)


def user_exists(username: str) -> bool:
    """Check if username already exists"""
    profiles = load_profiles()
    for user_data in profiles.values():
        if user_data["username"] == username:
            return True
    return False


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


# API endpoints
@app.post("/users/create", response_model=UserResponse)
async def create_user(profile: UserProfile):
    """
    Create a new user account

    BENEFITS: Secure account creation for personalized tracking experience
    COSTS: Requires unique username; data stored locally
    """
    # Validate unique username
    if user_exists(profile.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    # Validate password strength (basic check)
    if len(profile.password) < 6:
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters long"
        )

    # Create new user
    user_id = str(uuid.uuid4())
    new_user = {
        "user_id": user_id,
        "username": profile.username,
        "password": hash_password(profile.password),
        "created_at": str(datetime.now()),
    }

    # Save to storage
    profiles = load_profiles()
    profiles[user_id] = new_user
    save_profiles(profiles)

    # Return response (excluding password)
    return UserResponse(
        user_id=user_id,
        username=new_user["username"],
        created_at=new_user["created_at"],
    )


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user profile by ID"""
    profiles = load_profiles()
    if user_id not in profiles:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = profiles[user_id]
    return UserResponse(
        user_id=user_data["user_id"],
        username=user_data["username"],
        created_at=user_data["created_at"],
    )


@app.get("/users/username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str):
    """Get user profile by username"""
    profiles = load_profiles()
    for user_data in profiles.values():
        if user_data["username"] == username:
            return UserResponse(
                user_id=user_data["user_id"],
                username=user_data["username"],
                created_at=user_data["created_at"],
            )
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users/login", response_model=LoginResponse)
async def login_user(credentials: LoginRequest):
    """Authenticate a user with username and password"""
    profiles = load_profiles()
    for user_data in profiles.values():
        if user_data["username"] == credentials.username:
            if verify_password(credentials.password, user_data["password"]):
                return LoginResponse(
                    message="Login successful",
                    user_id=user_data["user_id"],
                    username=user_data["username"],
                )
            else:
                raise HTTPException(status_code=401, detail="Invalid password")

    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users/delete", response_model=DeleteResponse)
async def delete_user(user_info: DeleteRequest):
    """Delete a user with their username and UUID"""
    profiles = load_profiles()

    if user_exists(user_info.username):
        try:
            del profiles[user_info.user_id]

            save_profiles(profiles)

            return DeleteResponse(
                message=f"Deleted account for user {user_info.username}",
                username=user_info.username,
            )
        except KeyError:
            raise HTTPException(status_code=401, detail="Invalid user_info")
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "profile_management"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
