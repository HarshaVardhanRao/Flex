# MITS - FLEX Application

This application consists of a Django backend API and a React frontend.

## Setup Instructions

### Backend Setup (Django)

1. Navigate to the Backend directory:
   ```
   cd Backend
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Apply database migrations:
   ```
   python manage.py migrate
   ```

4. Start the Django server:
   ```
   python manage.py runserver 8000
   ```

The backend API will be available at http://localhost:8000/api/

### Frontend Setup (React)

1. Navigate to the Frontend directory:
   ```
   cd Frontend
   ```

2. Install the required npm packages:
   ```
   npm install
   ```

3. Start the React development server:
   ```
   npm start
   ```

The frontend will be available at http://localhost:3000/

## API Endpoints

The following API endpoints are available:

- `GET /api/students/`: List all students
- `GET /api/student/<rollno>/`: Get details of a specific student
- `GET /api/projects/`: List all projects
- `GET /api/certificates/`: List all certificates

### Authentication Endpoints

- `POST /api/login/`: Login with username and password
- `POST /api/logout/`: Logout the currently authenticated user
- `GET /api/current-user/`: Get the currently authenticated user's details

## Frontend Routes

- `/login`: Login page
- `/dashboard`: Main dashboard (requires authentication)
- `/`: Redirects to dashboard

## Technologies Used

- **Backend**: Django, Django REST Framework
- **Frontend**: React, React Router, Tailwind CSS
- **Data Storage**: PostgreSQL / SQLite3

## Notes

- CORS is enabled for http://localhost:3000 to allow the frontend to communicate with the backend API.
- Authentication is handled using Django's session authentication.
- The frontend uses context API for state management.
