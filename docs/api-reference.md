⚙️ Environment Variables

FLASK_APP=app.py
SECRET_KEY=change-me
JWT_SECRET_KEY=change-me-too
DATABASE_URL=sqlite:///db.sqlite3


🔌 API Endpoints

POST /auth/register — register new user

POST /auth/login — login and get JWT

GET /beats — list beats

POST /beats — create beat

PUT /beats/:id — update beat

DELETE /beats/:id — delete beat

📂 Project Structure

backend/
  app.py
  models/
  routes/
  utils/
  requirements.txt
  README.md

🛡 License
MIT License


---

## **Backend – docs/api-reference.md**
```markdown
# API Reference — Beat Lab Backend

## Authentication
### Register
**POST** `/auth/register`  
Request body:
```json
{
  "username": "john",
  "password": "123456"
}

{
  "message": "User registered successfully"
}

Login
POST /auth/login
Request body:
{
  "username": "john",
  "password": "123456"
}


Response:

{
  "access_token": "jwt_token_here"
}

Beats
List Beats
GET /beats → Returns list of beats.

Create Beat
POST /beats → Creates a new beat (requires JWT).

Update Beat
PUT /beats/:id → Updates beat by ID.

Delete Beat
DELETE /beats/:id → Deletes beat by ID.