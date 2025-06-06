import os
import uuid
from typing import Optional
from PIL import Image
from app.config import settings

def save_upload_file(file, upload_dir: str = None) -> str:
    """Save an uploaded file and return the file path"""
    if upload_dir is None:
        upload_dir = settings.UPLOAD_DIR
    
    # Create upload directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    return file_path

def resize_image(image_path: str, max_size: tuple = (800, 600)) -> str:
    """Resize an image to fit within max_size while maintaining aspect ratio"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path, optimize=True, quality=85)
        return image_path
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image_path

def format_time_ago(dt: datetime) -> str:
    """Format a datetime as 'time ago' string"""
    from datetime import datetime
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return "Just now"