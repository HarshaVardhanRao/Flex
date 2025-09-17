# MITS - FLEX Application

MITS-FLEX is a comprehensive student management and tracking system built with Django. It provides features for managing student profiles, projects, certifications, placements, and dynamic form creation for academic institutions.

## Features

- **Student Management**: Track student profiles, academic progress, and achievements
- **Project Tracking**: Manage student projects with technology tags and contributors
- **Certification Management**: Record technical, language, and co-curricular certificates
- **Placement Dashboard**: Monitor placement statistics and offers
- **Dynamic Forms**: Create and manage custom forms for data collection
- **LeetCode Integration**: Track coding progress through LeetCode profiles
- **FlexOn Analytics**: Natural language query interface for data insights
- **Multi-role Support**: Different dashboards for students, faculty, and administrators

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Backend Setup (Django)

1. Navigate to the Backend directory:
   ```bash
   cd Backend
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

The application will be available at http://localhost:8000/

## Application Structure

```
Backend/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── flex/                  # Main Django project
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI application
├── flexapp/              # Main Django app
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── urls.py           # App URL patterns
│   ├── forms.py          # Django forms
│   ├── serializers.py    # API serializers
│   ├── templates/        # HTML templates
│   └── migrations/       # Database migrations
├── static/               # Static files (CSS, JS, images)
├── staticfiles/          # Collected static files
└── media/                # User uploaded files
```

## Key Features & URLs

### Authentication & User Management
- `/`: Login page
- `/register/`: User registration
- `/verify_otp/`: OTP verification
- `/logout/`: Logout

### Dashboards
- `/dashboard/`: Student dashboard
- `/faculty_dashboard/`: Faculty dashboard  
- `/admin_dashboard/`: Administrator dashboard
- `/dashboard/placement/`: Placement analytics dashboard

### Forms & Data Collection
- `/create/`: Create dynamic forms
- `/forms/`: List created forms
- `/assigned/`: View assigned forms
- `/fill/<form_id>/`: Fill out a specific form

### Analytics
- `/dashboard/placement/`: Placement dashboard with charts
- `/flexon_dashboard/`: Natural language query interface

### API Endpoints
- `/api/students/`: List all students
- `/api/student/<rollno>/`: Get specific student details
- `/api/projects/`: List all projects
- `/api/certificates/`: List all certificates
- `/api/login/`: API login endpoint
- `/api/current-user/`: Get current user details

## Core Models

- **Student**: Extended user model with academic details
- **Projects**: Student project tracking with technologies and contributors
- **Certificate**: Various types of certifications and achievements
- **LeetCode**: Programming contest statistics
- **PlacementOffer**: Job placement tracking
- **FillOutForm**: Dynamic form creation system
- **Technology**: Technology tags for projects

## Technologies Used

- **Backend Framework**: Django 5.0.8
- **API**: Django REST Framework
- **Database**: SQLite3 (development) / PostgreSQL (production ready)
- **Frontend Styling**: Bootstrap 5.3.3, Bootstrap Icons
- **Email**: SMTP integration for OTP verification
- **Charts**: Chart.js for analytics visualization
- **CORS**: django-cors-headers for API access

## Configuration

### Static Files
- Static files are served from `/static/`
- Collected static files are in `/staticfiles/`
- User uploads are stored in `/media/`

## Development Notes

- **Authentication**: Uses Django's built-in authentication with custom user model
- **Session Management**: Session-based authentication for web interface
- **CSRF Protection**: Enabled for form submissions
- **Theme Support**: Built-in light/dark theme toggle
- **Responsive Design**: Mobile-friendly interface
- **API Documentation**: Available at `/api/` endpoint

## Security Features

- CSRF protection on all forms
- OTP-based email verification
- Session-based authentication
- Safe query execution in FlexOn analytics
- Input validation and sanitization

## Testing

Run the test suite:
```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure functionality
5. Submit a pull request

## License

This project is developed for MITS (Madanapalle Institute of Technology & Science) academic purposes.