from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
import os

from core.database import get_db, init_db
from core.security import create_access_token, verify_token, get_password_hash, verify_password
from models.schemas import UserCreate, PostCreate, User, Post
from services.business import UserService, PostService, ConnectionService
from core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="LinkedIn Clone",
    description="A professional networking platform",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Security
security = HTTPBearer(auto_error=False)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Dependency to get current user
async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from token or session"""
    token = None
    
    # Try to get token from Authorization header
    if credentials:
        token = credentials.credentials
    
    # Try to get token from session cookie
    if not token:
        token = request.session.get("access_token")
    
    if not token:
        return None
    
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id:
            user_service = UserService(db)
            return user_service.get_user_by_id(int(user_id))
    except:
        return None
    
    return None

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "linkedin-clone"}

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user:
        # Get recent posts for feed
        post_service = PostService(db)
        posts = post_service.get_recent_posts(limit=20)
        
        return templates.TemplateResponse(
            "feed.html",
            {
                "request": request,
                "current_user": current_user,
                "posts": posts,
                "page_title": "Feed"
            }
        )
    else:
        return templates.TemplateResponse(
            "landing.html",
            {"request": request, "page_title": "Welcome to LinkedIn Clone"}
        )

# Login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "page_title": "Sign In"}
    )

# Login endpoint
@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user = user_service.authenticate_user(email, password)
    
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Invalid email or password",
                "page_title": "Sign In"
            }
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Store token in session
    request.session["access_token"] = access_token
    
    return RedirectResponse(url="/", status_code=302)

# Register page
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "page_title": "Join LinkedIn Clone"}
    )

# Register endpoint
@app.post("/register")
async def register(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    headline: str = Form(""),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    # Check if user already exists
    if user_service.get_user_by_email(email):
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Email already registered",
                "page_title": "Join LinkedIn Clone"
            }
        )
    
    # Create new user
    user_data = UserCreate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        headline=headline
    )
    
    try:
        user = user_service.create_user(user_data)
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Store token in session
        request.session["access_token"] = access_token
        
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Registration failed. Please try again.",
                "page_title": "Join LinkedIn Clone"
            }
        )

# Logout endpoint
@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

# Profile page
@app.get("/profile/{user_id}", response_class=HTMLResponse)
async def profile(
    request: Request,
    user_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    post_service = PostService(db)
    connection_service = ConnectionService(db)
    
    profile_user = user_service.get_user_by_id(user_id)
    if not profile_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's posts
    user_posts = post_service.get_posts_by_user(user_id)
    
    # Check connection status
    is_connected = False
    connection_pending = False
    if current_user and current_user.id != user_id:
        is_connected = connection_service.are_connected(current_user.id, user_id)
        connection_pending = connection_service.is_connection_pending(current_user.id, user_id)
    
    return templates.TemplateResponse(
        "profile/profile.html",
        {
            "request": request,
            "current_user": current_user,
            "profile_user": profile_user,
            "posts": user_posts,
            "is_connected": is_connected,
            "connection_pending": connection_pending,
            "page_title": f"{profile_user.first_name} {profile_user.last_name}"
        }
    )

# My profile page
@app.get("/my-profile", response_class=HTMLResponse)
async def my_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return RedirectResponse(url=f"/profile/{current_user.id}", status_code=302)

# Create post endpoint
@app.post("/posts/create")
async def create_post(
    request: Request,
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    post_service = PostService(db)
    post_data = PostCreate(content=content, user_id=current_user.id)
    
    try:
        post_service.create_post(post_data)
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        # Handle error - for now just redirect back
        return RedirectResponse(url="/", status_code=302)

# Network page
@app.get("/network", response_class=HTMLResponse)
async def network(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    user_service = UserService(db)
    connection_service = ConnectionService(db)
    
    # Get connections
    connections = connection_service.get_connections(current_user.id)
    
    # Get suggested connections (users not connected)
    suggested = user_service.get_suggested_connections(current_user.id, limit=10)
    
    return templates.TemplateResponse(
        "network/network.html",
        {
            "request": request,
            "current_user": current_user,
            "connections": connections,
            "suggested": suggested,
            "page_title": "My Network"
        }
    )

# Send connection request
@app.post("/connections/send/{user_id}")
async def send_connection_request(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    connection_service = ConnectionService(db)
    
    try:
        connection_service.send_connection_request(current_user.id, user_id)
    except Exception as e:
        pass  # Handle error silently for now
    
    return RedirectResponse(url="/network", status_code=302)

# Accept connection request
@app.post("/connections/accept/{user_id}")
async def accept_connection_request(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    connection_service = ConnectionService(db)
    
    try:
        connection_service.accept_connection_request(user_id, current_user.id)
    except Exception as e:
        pass  # Handle error silently for now
    
    return RedirectResponse(url="/network", status_code=302)

# Jobs page
@app.get("/jobs", response_class=HTMLResponse)
async def jobs(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "jobs/jobs.html",
        {
            "request": request,
            "current_user": current_user,
            "page_title": "Jobs"
        }
    )

# Messaging page
@app.get("/messaging", response_class=HTMLResponse)
async def messaging(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "messaging/messaging.html",
        {
            "request": request,
            "current_user": current_user,
            "page_title": "Messaging"
        }
    )

# Search endpoint
@app.get("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    q: str = "",
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = []
    if q:
        user_service = UserService(db)
        results = user_service.search_users(q)
    
    return templates.TemplateResponse(
        "search/results.html",
        {
            "request": request,
            "current_user": current_user,
            "query": q,
            "results": results,
            "page_title": f"Search: {q}" if q else "Search"
        }
    )

# Add session middleware
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Add CORS middleware for development
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)