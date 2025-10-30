from flask import send_from_directory
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pymysql
from pymysql.cursors import DictCursor
from functools import wraps
import os

# Initialize Flask app
app = Flask(__name__)

# Config
app.config.update({
    "MYSQL_HOST": "localhost",
    "MYSQL_USER": "root",
    "MYSQL_PASSWORD": "",
    "MYSQL_DB": "sciqus_intern",
    "JWT_SECRET_KEY": "super-secret-key"
})



bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# --- Helper to get DB connection ---
def get_db_connection():
    return pymysql.connect(
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DB"],
        cursorclass=DictCursor
    )

# --- Role decorator ---
def role_required(role):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT role FROM users WHERE user_id=%s", (identity,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row or row["role"] != role:
                return jsonify({"msg": "Forbidden"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

# --- Routes ---

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "email and password required"}), 400
    pw_hash = bcrypt.generate_password_hash(data['password']).decode()

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name,email,password_hash,role) VALUES (%s,%s,%s,%s)",
            (data.get('name'), data['email'], pw_hash, data.get('role', 'student'))
        )
        conn.commit()
        return jsonify({"msg": "Registered"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id,password_hash,role FROM users WHERE email=%s", (data.get('email'),))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row and bcrypt.check_password_hash(row["password_hash"], data.get('password')):
        token = create_access_token(identity=str(row["user_id"]))
        return jsonify({"access_token": token, "role": row["role"]})
    return jsonify({"msg": "Invalid credentials"}), 401

@app.route('/courses', methods=['POST'])
@role_required('admin')
def create_course():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO courses (course_name,course_code,course_duration) VALUES (%s,%s,%s)",
        (data.get('course_name'), data.get('course_code'), data.get('course_duration'))
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"msg": "Course created"}), 201

@app.route('/students', methods=['POST'])
@role_required('admin')
def add_student():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_id FROM courses WHERE course_id=%s", (data.get('course_id'),))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"msg": "Course not found"}), 400
    pw_hash = bcrypt.generate_password_hash(data.get('password', 'student123')).decode()
    cur.execute(
        "INSERT INTO users (name,email,password_hash,role,course_id) VALUES (%s,%s,%s,'student',%s)",
        (data.get('name'), data.get('email'), pw_hash, data.get('course_id'))
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"msg": "Student added"}), 201

@app.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    identity = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE user_id=%s", (identity,))
    role = cur.fetchone()["role"]
    if role == 'student':
        cur.execute("""
            SELECT u.user_id,u.name,u.email,c.course_id,c.course_name,c.course_code
            FROM users u LEFT JOIN courses c ON u.course_id=c.course_id
            WHERE u.user_id=%s
        """, (identity,))
    else:
        cur.execute("""
            SELECT u.user_id,u.name,u.email,c.course_id,c.course_name,c.course_code
            FROM users u LEFT JOIN courses c ON u.course_id=c.course_id
        """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "user_id": r["user_id"],
            "name": r["name"],
            "email": r["email"],
            "course": {
                "course_id": r["course_id"],
                "course_name": r["course_name"],
                "course_code": r["course_code"]
            } if r["course_id"] else None
        })
    return jsonify(result)

@app.route('/students/<int:student_id>', methods=['PUT'])
@role_required('admin')
def update_student(student_id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    if data.get('course_id'):
        cur.execute("SELECT 1 FROM courses WHERE course_id=%s", (data['course_id'],))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"msg": "Course not found"}), 400
    cur.execute(
        "UPDATE users SET name=%s, email=%s, course_id=%s WHERE user_id=%s",
        (data.get('name'), data.get('email'), data.get('course_id'), student_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"msg": "Updated"})

@app.route('/students/<int:student_id>', methods=['DELETE'])
@role_required('admin')
def delete_student(student_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id=%s AND role='student'", (student_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"msg": "Deleted"})


import os
from flask import send_from_directory

FRONTEND_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(FRONTEND_FOLDER, path)



if __name__ == '__main__':
    app.run(debug=True)
