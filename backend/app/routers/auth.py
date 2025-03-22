from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str

@router.post("/login", response_model=UserResponse)
async def login(request: LoginRequest):
    """
    Mock login endpoint for hackathon purposes
    """
    # For hackathon, we'll just return a mock user
    # In a real app, you would integrate with Stytch here
    user_id = str(uuid.uuid4())
    
    return {
        "id": user_id,
        "email": request.email,
        "name": "Demo User",
        "role": "legal_professional"
    }