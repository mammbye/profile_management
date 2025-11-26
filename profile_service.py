from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import uuid
from typing import Dict, Optional, Tuple
import os
import bcrypt
from datetime import datetime

app = FastAPI(title="Profile Management Microservice")

# Add CORS middleware to handle OPTIONS requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins.
    # In production, specify exact origins.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

PROFILES_FILE = os.path.join(os.path.dirname(__file__), "user_profiles.json")


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


def check_username_available(username: str) -> None:
    """Raise HTTPException if username already exists"""
    profiles = load_profiles()
    for user_data in profiles.values():
        if user_data["username"] == username:
            raise HTTPException(
                status_code=400, detail="Username already exists"
            )


def find_user_by_username(username: str) -> Optional[Tuple[str, dict]]:
    """Find user by username. Returns (user_id, user_data) or None"""
    profiles = load_profiles()
    for user_id, user_data in profiles.items():
        if user_data["username"] == username:
            return user_id, user_data
    return None


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


def save_user(profile: UserProfile) -> dict:
    """Save user data to JSON file and return the created user data"""
    profiles = load_profiles()
    user_id = str(uuid.uuid4())
    profiles[user_id] = {
        "user_id": user_id,
        "username": profile.username,
        "password": hash_password(profile.password),
        "created_at": str(datetime.now()),
    }
    save_profiles(profiles)
    return profiles[user_id]


def validate_password(password: str) -> None:
    """Validate a password"""
    if len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters long"
        )


@app.post("/users/create", response_model=UserResponse)
async def create_user(profile: UserProfile):
    """Create a new user account"""
    check_username_available(profile.username)
    validate_password(profile.password)
    new_user = save_user(profile)
    return UserResponse(
        user_id=new_user["user_id"],
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
    result = find_user_by_username(username)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_id, user_data = result
    return UserResponse(
        user_id=user_data["user_id"],
        username=user_data["username"],
        created_at=user_data["created_at"],
    )


@app.post("/users/login", response_model=LoginResponse)
async def login_user(credentials: LoginRequest):
    """Authenticate a user with username and password"""
    result = find_user_by_username(credentials.username)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id, user_data = result
    if not verify_password(credentials.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    return LoginResponse(
        message="Login successful",
        user_id=user_data["user_id"],
        username=user_data["username"],
    )


@app.post("/users/delete", response_model=DeleteResponse)
async def delete_user(user_info: DeleteRequest):
    """Delete a user with their username and UUID"""
    profiles = load_profiles()
    
    if user_info.user_id not in profiles:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = profiles[user_info.user_id]
    if user_data["username"] != user_info.username:
        raise HTTPException(status_code=401, detail="Invalid user_info")
    
    del profiles[user_info.user_id]
    save_profiles(profiles)
    
    return DeleteResponse(
        message=f"Deleted account for user {user_info.username}",
        username=user_info.username,
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "profile_management"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
