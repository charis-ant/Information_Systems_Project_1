# Student Management REST API

A university project developed for the Information Systems course.

This project implements a REST API for managing student records using **Python**, **Flask**, **MongoDB** and **Docker**. The application demonstrates database integration, user authentication, session management, and CRUD operations through a set of HTTP endpoints.

## Overview

The system manages two MongoDB collections:

- **Students**: student records and academic information. Populated using the provided `students.json` file
- **Users**: application users used for authentication. Populated through the `/createUser` endpoint during application usage

The API allows authenticated users to:

- Create user accounts
- Login and create authenticated sessions
- Retrieve student information
- Query students based on age criteria
- Retrieve student address details
- Update student records by adding courses and grades
- View passed courses
- Delete student records

## Features

### Authentication
- User registration
- User login
- Session-based authentication using UUIDs

### Student Management
- Retrieve student information by email
- Retrieve student address details
- Delete student records

### Filtering & Queries
- Retrieve students born in 1991
- Retrieve students born in 1991 or earlier
- Retrieve passed courses for a student

### Data Updates
- Add courses and grades to a student record

## Technologies Used

- Python
- Flask
- MongoDB
- PyMongo
- Docker
- REST APIs
- JSON

## Project Structure

```text
.
├── app.py
├── students.json
├── README.md
└── assets
```

## Setup

### 1. Start Docker

```bash
sudo dockerd
```

### 2. Pull MongoDB Image

```bash
sudo docker pull mongo
sudo docker pull mongo:4.0.4
```

### 3. Create MongoDB Container

```bash
sudo docker run -d -p 27017:27017 --name mongodb mongo:4.0.4
```

### 4. Start MongoDB

```bash
sudo docker start mongodb
```

### 5. Create Database and Import Data

Open a MongoDB shell:

```bash
sudo docker exec -it mongodb mongo
```

Create the database:

```javascript
use InfoSys
```

Import data file:

```bash
sudo docker cp students.json mongodb:/students.json
docker exec -it mongodb mongoimport --db=InfoSys --collection=Students --file=students.json
```

### 6. Run the Application

```bash
python3 app.py
```
The application will start locally and expose the available REST endpoints.

## API Endpoints

| Method | Endpoint | Description |
|----------|----------|----------|
| POST | `/createUser` | Register a new user |
| POST | `/login` | Authenticate a user |
| GET | `/getStudent` | Retrieve a student by email |
| GET | `/getStudents/thirties` | Retrieve students born in 1991 |
| GET | `/getStudents/oldies` | Retrieve students born in 1991 or earlier |
| GET | `/getStudentAddress` | Retrieve student address information |
| DELETE | `/deleteStudent` | Delete a student |
| PATCH | `/addCourses` | Add courses and grades |
| GET | `/getPassedCourses` | Retrieve successfully passed courses |

# Example Usage

### Create User

```bash
curl -X POST localhost:5000/createUser \
-d '{"username":"user1", "password":"123456789"}' \
-H Content-Type:application/json
```

### Login

```bash
curl -X POST localhost:5000/login \
-d '{"username":"user1", "password":"1234567897"}' \
-H Content-Type:application/json
```

### Get Student

```bash
curl -X GET localhost:5000/getStudent \
-d '{"email":"herreraware@ontagene.com"}' \
-H "authorization: 592b6b0e-b316-11eb-b18c-00155da5c9a2" \
-H Content-Type:application/json
```

### Get students (thirties)
```bash
curl -X GET localhost:5000/getStudents/thirties \
-H "authorization: 592b6b0e-b316-11eb-b18c-00155da5c9a2" \
-H Content-Type:application/json
```

### Get students (oldies)
```bash
curl -X GET localhost:5000/getStudents/oldies \
-H "authorization: 592b6b0e-b316-11eb-b18c-00155da5c9a2" \
-H Content-Type:application/json
```

### Get student address
```bash
curl -X GET localhost:5000/getStudentAddress \
-d '{"email":"herreraware@ontagene.com"}' \
-H "authorization: 592b6b0e-b316-11eb-b18c-00155da5c9a2" \
-H Content-Type:application/json
```

### Delete student
```bash
curl -X DELETE localhost:5000/deleteStudent \
-d '{"email":"herreraware@ontagene.com"}' \
-H "authorization: 592b6b0e-b316-11eb-b18c-00155da5c9a2" \
-H Content-Type:application/json
```

### Add courses
```bash
curl -X PATCH localhost:5000/addCourses \
-d '{"email":"middletondelacruz@ontagene.com", "courses":[{"InfoSys":10}, {"XML":4}, {"Networks":5}]}' \
-H "authorization: 592b6b0e-b316-11eb-b18c-00155da5c9a2" \
-H Content-Type:application/json
```

### Get passed courses
```bash
curl -X GET localhost:5000/getPassedCourses \
-d '{"email":"middletondelacruz@ontagene.com"}' \
-H "authorization: 592b6b0e-b316-11eb-b18c-00155da5c9a2"
-H Content-Type:application/json
```

## Learning Outcomes

- REST API development
- Backend architecture
- HTTP methods (GET, POST, PATCH, DELETE)
- Authentication and session management
- MongoDB document databases
- PyMongo database operations
- Docker containerization

## Academic Context

This project was developed during my BSc studies in Computer Science as part of the Information Systems course. The goal was to design a backend service capable of managing and querying student data stored in a MongoDB database while applying RESTful API principles and authentication mechanisms.
