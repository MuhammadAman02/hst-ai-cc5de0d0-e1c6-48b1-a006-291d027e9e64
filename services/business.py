from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import List, Optional
from datetime import datetime

from core.database import User, Post, Connection
from core.security import get_password_hash, verify_password
from models.schemas import UserCreate, PostCreate

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            headline=user_data.headline or ""
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    def search_users(self, query: str, limit: int = 20) -> List[User]:
        """Search users by name or headline"""
        return self.db.query(User).filter(
            or_(
                User.first_name.ilike(f"%{query}%"),
                User.last_name.ilike(f"%{query}%"),
                User.headline.ilike(f"%{query}%")
            )
        ).limit(limit).all()
    
    def get_suggested_connections(self, user_id: int, limit: int = 10) -> List[User]:
        """Get suggested connections for a user"""
        # Get users that are not connected and not the current user
        connected_user_ids = self.db.query(Connection.receiver_id).filter(
            Connection.sender_id == user_id,
            Connection.status == "accepted"
        ).union(
            self.db.query(Connection.sender_id).filter(
                Connection.receiver_id == user_id,
                Connection.status == "accepted"
            )
        ).subquery()
        
        return self.db.query(User).filter(
            User.id != user_id,
            ~User.id.in_(connected_user_ids)
        ).limit(limit).all()

class PostService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_post(self, post_data: PostCreate) -> Post:
        """Create a new post"""
        db_post = Post(
            content=post_data.content,
            user_id=post_data.user_id
        )
        
        self.db.add(db_post)
        self.db.commit()
        self.db.refresh(db_post)
        return db_post
    
    def get_recent_posts(self, limit: int = 20) -> List[Post]:
        """Get recent posts for feed"""
        return self.db.query(Post).order_by(desc(Post.created_at)).limit(limit).all()
    
    def get_posts_by_user(self, user_id: int, limit: int = 20) -> List[Post]:
        """Get posts by a specific user"""
        return self.db.query(Post).filter(
            Post.user_id == user_id
        ).order_by(desc(Post.created_at)).limit(limit).all()

class ConnectionService:
    def __init__(self, db: Session):
        self.db = db
    
    def send_connection_request(self, sender_id: int, receiver_id: int) -> Connection:
        """Send a connection request"""
        # Check if connection already exists
        existing = self.db.query(Connection).filter(
            or_(
                and_(Connection.sender_id == sender_id, Connection.receiver_id == receiver_id),
                and_(Connection.sender_id == receiver_id, Connection.receiver_id == sender_id)
            )
        ).first()
        
        if existing:
            raise ValueError("Connection already exists")
        
        connection = Connection(
            sender_id=sender_id,
            receiver_id=receiver_id,
            status="pending"
        )
        
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection
    
    def accept_connection_request(self, sender_id: int, receiver_id: int) -> Connection:
        """Accept a connection request"""
        connection = self.db.query(Connection).filter(
            Connection.sender_id == sender_id,
            Connection.receiver_id == receiver_id,
            Connection.status == "pending"
        ).first()
        
        if not connection:
            raise ValueError("Connection request not found")
        
        connection.status = "accepted"
        connection.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(connection)
        return connection
    
    def are_connected(self, user1_id: int, user2_id: int) -> bool:
        """Check if two users are connected"""
        connection = self.db.query(Connection).filter(
            or_(
                and_(Connection.sender_id == user1_id, Connection.receiver_id == user2_id),
                and_(Connection.sender_id == user2_id, Connection.receiver_id == user1_id)
            ),
            Connection.status == "accepted"
        ).first()
        
        return connection is not None
    
    def is_connection_pending(self, sender_id: int, receiver_id: int) -> bool:
        """Check if there's a pending connection request"""
        connection = self.db.query(Connection).filter(
            Connection.sender_id == sender_id,
            Connection.receiver_id == receiver_id,
            Connection.status == "pending"
        ).first()
        
        return connection is not None
    
    def get_connections(self, user_id: int) -> List[User]:
        """Get all connections for a user"""
        # Get accepted connections where user is sender
        sender_connections = self.db.query(User).join(
            Connection, User.id == Connection.receiver_id
        ).filter(
            Connection.sender_id == user_id,
            Connection.status == "accepted"
        )
        
        # Get accepted connections where user is receiver
        receiver_connections = self.db.query(User).join(
            Connection, User.id == Connection.sender_id
        ).filter(
            Connection.receiver_id == user_id,
            Connection.status == "accepted"
        )
        
        # Combine and return
        return sender_connections.union(receiver_connections).all()