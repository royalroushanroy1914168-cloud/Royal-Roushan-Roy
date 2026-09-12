from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3, os, secrets, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

DEPARTMENT_EMAIL = os.environ.get("DEPARTMENT_EMAIL", "department@nagardrishti.gov.in")
DEPARTMENT_PASSWORD_HASH = os.environ.get(
    "DEPARTMENT_PASSWORD_HASH",
    generate_password_hash("Department@123")
)

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_id TEXT UNIQUE NOT NULL,
        citizen_id INTEGER,
        citizen_name TEXT NOT NULL,
        contact TEXT,
        problem_type TEXT NOT NULL,
        description TEXT NOT NULL,
        location TEXT,
        latitude REAL,
        longitude REAL,
        image_path TEXT,
        priority_score INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Pending',
        assigned_department TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(citizen_id) REFERENCES users(id)
    );
    """)
    conn.commit()
    conn.close()

def make_token(prefix):
    return f"{prefix}_{secrets.token_urlsafe(24)}"

citizen_tokens = {}
department_tokens = set()

def citizen_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        user_id = citizen_tokens.get(token)
        if not user_id:
            return jsonify({"error": "Citizen authentication required"}), 401
        request.user_id = user_id
        return fn(*args, **kwargs)
    return wrapper

def department_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if token not in department_tokens:
            return jsonify({"error": "Department authentication required"}), 401
        return fn(*args, **kwargs)
    return wrapper

def priority(problem_type, description):
    high = {"Road Accident Hazard", "Blocked Drain", "Water Leakage"}
    medium = {"Pothole", "Damaged Road", "Broken Streetlight"}
    if problem_type in high:
        return 90
    if problem_type in medium:
        return 70
    if len(description) > 200:
        return 60
    return 50

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "NagarDrishti API"})

@app.post("/api/register")
def register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400
    conn = db()
    try:
        conn.execute(
            "INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)",
            (name, email, generate_password_hash(password), datetime.datetime.now().isoformat())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Email already registered"}), 409
    conn.close()
    return jsonify({"message": "Registration successful"})

@app.post("/api/login")
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    conn = db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401
    token = make_token("citizen")
    citizen_tokens[token] = user["id"]
    return jsonify({"token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}})

@app.post("/api/department/login")
def department_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if email != DEPARTMENT_EMAIL or not check_password_hash(DEPARTMENT_PASSWORD_HASH, password):
        return jsonify({"error": "Invalid department credentials"}), 401
    token = make_token("department")
    department_tokens.add(token)
    return jsonify({"token": token, "department": "Civic Department"})

@app.post("/api/reports")
@citizen_required
def create_report():
    problem_type = request.form.get("problem_type", "").strip()
    description = request.form.get("description", "").strip()
    location = request.form.get("location", "").strip()
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    contact = request.form.get("contact", "").strip()
    image = request.files.get("image")

    if not problem_type or not description:
        return jsonify({"error": "Problem type and description are required"}), 400

    conn = db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (request.user_id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    tracking_id = "NGR-" + datetime.datetime.now().strftime("%Y%m%d") + "-" + secrets.token_hex(3).upper()
    image_path = None
    if image and image.filename:
        safe_name = secrets.token_hex(8) + "_" + os.path.basename(image.filename)
        image.save(os.path.join(UPLOAD_DIR, safe_name))
        image_path = f"/api/uploads/{safe_name}"

    score = priority(problem_type, description)
    now = datetime.datetime.now().isoformat()
    conn.execute("""
        INSERT INTO reports(
            tracking_id,citizen_id,citizen_name,contact,problem_type,description,
            location,latitude,longitude,image_path,priority_score,status,
            created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        tracking_id, user["id"], user["name"], contact, problem_type, description,
        location, float(latitude) if latitude else None,
        float(longitude) if longitude else None, image_path, score, "Pending", now, now
    ))
    conn.commit()
    report_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()

    return jsonify({
        "message": "Complaint registered successfully",
        "tracking_id": tracking_id,
        "report_id": report_id,
        "status": "Pending",
        "priority_score": score
    }), 201

@app.get("/api/reports/mine")
@citizen_required
def my_reports():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM reports WHERE citizen_id=? ORDER BY id DESC", (request.user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.get("/api/reports/track/<tracking_id>")
def track(tracking_id):
    conn = db()
    row = conn.execute("SELECT * FROM reports WHERE tracking_id=?", (tracking_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Tracking ID not found"}), 404
    data = dict(row)
    data.pop("contact", None)
    data.pop("citizen_id", None)
    return jsonify(data)

@app.get("/api/department/reports")
@department_required
def department_reports():
    conn = db()
    rows = conn.execute("SELECT * FROM reports ORDER BY priority_score DESC, id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.patch("/api/department/reports/<int:report_id>")
@department_required
def update_report(report_id):
    data = request.get_json() or {}
    status = data.get("status")
    assigned = data.get("assigned_department")
    allowed = {"Pending", "Assigned", "In Progress", "Resolved"}
    if status not in allowed:
        return jsonify({"error": "Invalid status"}), 400

    conn = db()
    cur = conn.execute(
        "UPDATE reports SET status=?, assigned_department=?, updated_at=? WHERE id=?",
        (status, assigned, datetime.datetime.now().isoformat(), report_id)
    )
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return jsonify({"error": "Report not found"}), 404
    return jsonify({"message": "Complaint updated successfully"})

@app.get("/api/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_DIR, filename)

init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
