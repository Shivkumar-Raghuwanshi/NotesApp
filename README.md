# Note Taking and Sharing App

This is a RESTful API built with Django and Django REST Framework for a note-taking and sharing application. Users can create, read, update their notes, as well as share notes with other users. The API also keeps track of the history of changes made to each note, allowing users to view the previous versions of their notes.

## Table of Contents

- [Features](#features)
- [User Management](#user-management)
- [Note Management](#note-management)
- [Note History](#note-history)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
 - [Authentication](#authentication)
 - [Users](#users)
 - [Notes](#notes)
- [Request and Response Examples](#request-and-response-examples)
 - [Login](#login)
 - [Create a New Note](#create-a-new-note)
 - [Share a Note](#share-a-note)
 - [Update a Note](#update-a-note)
 - [Retrieve Note History](#retrieve-note-history)
- [Testing](#testing)

## Features

### User Management

- **User Registration**: Users can register by providing a username, email, and password.
- **User Authentication**: Users can authenticate using JSON Web Tokens (JWT) to access protected routes.

### Note Management

- **Create Notes**: Authenticated users can create new notes with a title and content.
- **Read Notes**: Users can retrieve a list of all notes they own or have been shared with them. They can also retrieve the details of a specific note.
- **Update Notes**: Users can update the title and content of their own notes or notes shared with them.
- **Share Notes**: Users can share their notes with other registered users.

### Note History

- **Track Changes**: The API keeps track of all changes made to a note, including additions, updates, and deletions.
- **View Note History**: Users can view the history of changes made to a specific note, including the line numbers, old content, new content, operation type (addition, update, or deletion), timestamp, and the user who made the change.

## Technologies Used

- **Python**: The programming language used for the backend.
- **Django**: A high-level Python web framework used for building the API.
- **Django REST Framework**: A powerful and flexible toolkit for building web APIs with Django.
- **Simple JWT**: A JSON Web Token authentication library for Django REST Framework.
- **SQLite3**: The database used for storing user, note, and note history data.

## Installation
1. Clone the repository: git clone https://github.com/Shivkumar-Raghuwanshi/NotesApp.git
2. Install the required dependencies: cd NotesApp pip install -r requirements.txt



3. Configure the database settings in the `settings.py` file.

4. Apply database migrations: py manage.py migrate
5. Start the development server: py manage.py runserver

The API will be accessible at http://localhost:8000/.

## API Endpoints

### Authentication

- `POST /api/token/`: Obtain JWT access and refresh tokens. Requires a valid username and password in the request body.
- `POST /api/token/refresh/`: Refresh JWT access token. Requires a valid refresh token in the request body.
- `POST /login/`: Authenticate an existing user. Requires a valid username and password in the request body, and the JWT token in the request headers.

### Users

- `POST /signup/`: Register a new user. Requires a username, email, and password in the request body.

### Notes

- `POST /notes/create/`: Create a new note. Requires a title and content in the request body. Authenticated user is set as the owner of the note.
- `GET /notes/`: List all notes owned or shared with the authenticated user.
- `GET /notes/<int:pk>/`: Retrieve details of a specific note. The user must be the owner or have been shared the note.
- `POST /notes/<int:pk>/share/`: Share a note with other users. Requires a list of usernames in the request body. The user must be the owner of the note.
- `PUT /notes/<int:pk>/update/`: Update a note. Requires a title and content in the request body. The user must be the owner or have been shared the note.
- `GET /notes/version-history/<int:note_pk>/`: Retrieve the history of changes made to a note. The user must be the owner or have been shared the note.

## Request and Response Examples

### Login

Request: 
POST /api/token/:
Content-Type: application/json
{
	"username": "newuser3", 
	"password": "newpassword3"
}
Response:
HTTP 200 OK
Content-Type: application/json

{
	"refresh": "<refresh_token>",
	"access": "<access_token>"
}

After obtaining the JWT access token, include it in the headers of the login POST request:
Request:
POST /login/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "username": "your_username",
    "password": "your_password"
}
Response:
HTTP 200 OK
Login successfully
### Create a New Note
Request:
POST /notes/create/
Content-Type: application/json
Authorization: Bearer <access_token>

{
"title": "My New Note",
"content": "This is the content of my new note."
}
Response:
HTTP 201 Created
Content-Type: application/json

{
"id": 1,
"title": "My New Note",
"content": "This is the content of my new note.",
"created_at": "2023-05-15T12:34:56.789Z",
"updated_at": "2023-05-15T12:34:56.789Z",
"owner": "your_username",
"shared_with": []
}

### Share a Note

Request: 
POST /notes/{id}/share/
Content-Type: application/json
Authorization: Bearer <access_token>

["user1", "user2"]

Response:

HTTP 200 OK
Content-Type: application/json

{
"message": "Note shared successfully.",
"owner": "your_username",
"shared_with": ["user1", "user2"]
}

### Update a Note

Request:
PUT /notes/{id}/update/
Content-Type: application/json
Authorization: Bearer <access_token>

{
"title": "My Updated Note",
"content": "This is the updated content of my note."
}

Response:
HTTP 200 OK
Content-Type: application/json

{
"id": 1,
"title": "My Updated Note",
"content": "This is the updated content of my note.",
"created_at": "2023-05-15T12:34:56.789Z",
"updated_at": "2023-05-15T13:45:12.345Z",
"owner": "your_username",
"shared_with": ["user1", "user2"]
}

### Retrieve Note History

Request:
GET /notes/version-history/{id}/
Authorization: Bearer <access_token>
Response:
HTTP 200 OK
Content-Type: application/json

[
{
"id": 1,
"note": 1,
"line_numbers": "1",
"old_content": "This is the content of my new note.",
"new_content": "This is the updated content of my note.",
"operation": "update",
"updated_at": "2023-05-15T13:45:12.345Z",
"updated_by": 1,
"updated_by_name": "your_username"
}
]
## Testing

To run the tests, use the following command: py manage.py test