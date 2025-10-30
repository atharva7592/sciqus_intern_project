# Backend - Sciqus Internship Starter
## What is included
- Flask API with endpoints for auth, courses, students
- MySQL schema (schema.sql)
## Quick setup
1. Install Python 3.9+ and MySQL server.
2. Create a database and import `schema.sql`.
3. Update environment variables or edit app.py defaults for DB credentials.
4. Create a virtualenv and install requirements:
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
5. Run the app:
   python app.py
## Notes
- The sample admin password hash in schema.sql is a placeholder. Register an admin via /auth/register or replace with a real bcrypt hash.
