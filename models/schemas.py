from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    headline: Optional[str] = ""
    summary: Optional[str] = ""
    location: Optional[str] = ""

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None

class User(UserBase):
    id: int
    profile_picture: Optional[str] = ""
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Post schemas
class PostBase(BaseModel):
    content: str

class PostCreate(PostBase):
    user_id: int

class Post(PostBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    author: User
    
    class Config:
        from_attributes = True

# Connection schemas
class ConnectionBase(BaseModel):
    sender_id: int
    receiver_id: int

class ConnectionCreate(ConnectionBase):
    pass

class Connection(ConnectionBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    sender: User
    receiver: User
    
    class Config:
        from_attributes = True

# Response schemas
class UserProfile(BaseModel):
    user: User
    posts: List[Post]
    connections_count: int
    is_connected: bool = False
    connection_pending: bool = False

class FeedResponse(BaseModel):
    posts: List[Post]
    has_more: bool = False

class SearchResponse(BaseModel):
    users: List[User]
    total: int