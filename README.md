# LinkedIn Clone

A professional networking platform built with FastAPI, featuring user profiles, connections, posts, messaging, and job listings.

## Features

- **User Authentication**: Secure registration and login system
- **Professional Profiles**: Comprehensive user profiles with photos and professional information
- **Social Networking**: Connect with other professionals and build your network
- **Content Sharing**: Create and share posts with your network
- **Job Board**: Browse and search for job opportunities
- **Messaging**: Real-time messaging between connected users
- **Search**: Find people and content across the platform

## Tech Stack

- **Backend**: FastAPI with Python 3.10+
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5 with Jinja2 templates
- **Authentication**: JWT tokens with bcrypt password hashing
- **Deployment**: Docker with Fly.io support

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linkedin-clone
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8000`

## Development

### Project Structure

```
linkedin-clone/
├── app/
│   ├── main.py              # FastAPI application and routes
│   └── config.py            # Application configuration
├── core/
│   ├── database.py          # Database models and connection
│   ├── security.py          # Authentication and security
│   └── utils.py             # Utility functions
├── models/
│   └── schemas.py           # Pydantic models
├── services/
│   └── business.py          # Business logic services
├── templates/               # HTML templates
├── static/                  # CSS, JS, and images
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── dockerfile              # Docker configuration
└── fly.toml                # Fly.io deployment config
```

### Key Components

- **User Management**: Registration, authentication, and profile management
- **Social Features**: Connections, posts, and networking
- **Job Board**: Job listings and search functionality
- **Messaging**: Real-time communication between users
- **Search**: Full-text search across users and content

### Database Models

- **User**: User profiles with authentication
- **Post**: User-generated content and posts
- **Connection**: Professional connections between users
- **Message**: Private messaging between connected users

## Deployment

### Docker

1. **Build the image**
   ```bash
   docker build -t linkedin-clone .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 linkedin-clone
   ```

### Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login to Fly**
   ```bash
   fly auth login
   ```

3. **Deploy the application**
   ```bash
   fly deploy
   ```

## Configuration

### Environment Variables

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT signing key (change in production)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: False)

### Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- CORS protection enabled
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `POST /logout` - User logout

### Social Features
- `GET /` - Home feed
- `POST /posts/create` - Create new post
- `GET /profile/{user_id}` - View user profile
- `POST /connections/send/{user_id}` - Send connection request

### Networking
- `GET /network` - View network and suggestions
- `GET /search` - Search users and content

### Jobs
- `GET /jobs` - Browse job listings

### Messaging
- `GET /messaging` - Messaging interface

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the code comments

## Roadmap

- [ ] Real-time notifications
- [ ] Advanced search filters
- [ ] Company pages
- [ ] Skills and endorsements
- [ ] Mobile app
- [ ] API rate limiting
- [ ] Advanced analytics
- [ ] Email notifications
- [ ] File sharing
- [ ] Video calls

---

Built with ❤️ using FastAPI and modern web technologies.