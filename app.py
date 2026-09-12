from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

import sqlite3
import os
import secrets
from datetime import datetime


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE = os.path.join(
    BASE_DIR,
    "database.db"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


app = Flask(__name__)

CORS(app)


# =========================================================
# DEPARTMENT LOGIN
# =========================================================
#
# Development credentials:
#
# Email:
# department@nagardrishti.gov.in
#
# Password:
# Department@123
#
# For production, use environment variables.
# =========================================================

DEPARTMENT_EMAIL = os.environ.get(
    "DEPARTMENT_EMAIL",
    "department@nagardrishti.gov.in"
)


DEPARTMENT_PASSWORD_HASH = os.environ.get(
    "DEPARTMENT_PASSWORD_HASH",
    generate_password_hash(
        "Department@123"
    )
)


# =========================================================
# TEMPORARY TOKEN STORAGE
# =========================================================

citizen_tokens = {}

department_tokens = set()


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():

    connection = get_db()

    cursor = connection.cursor()


    # -----------------------------------------------------
    # USERS TABLE
    # -----------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
        """
    )


    # -----------------------------------------------------
    # REPORTS TABLE
    # -----------------------------------------------------

    cursor.execute(
        """
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

            FOREIGN KEY (
                citizen_id
            )
            REFERENCES users(id)

        )
        """
    )


    connection.commit()

    connection.close()


# =========================================================
# TOKEN GENERATOR
# =========================================================

def generate_token(prefix):

    return (
        prefix
        + "_"
        + secrets.token_urlsafe(32)
    )


# =========================================================
# CITIZEN AUTHENTICATION DECORATOR
# =========================================================

def citizen_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        authorization = request.headers.get(
            "Authorization",
            ""
        )


        if not authorization.startswith(
            "Bearer "
        ):

            return jsonify({

                "error":
                "Citizen authentication required"

            }), 401


        token = authorization.replace(
            "Bearer ",
            "",
            1
        )


        user_id = citizen_tokens.get(
            token
        )


        if not user_id:

            return jsonify({

                "error":
                "Invalid or expired citizen token"

            }), 401


        request.user_id = user_id


        return function(
            *args,
            **kwargs
        )


    return wrapper


# =========================================================
# DEPARTMENT AUTHENTICATION DECORATOR
# =========================================================

def department_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        authorization = request.headers.get(
            "Authorization",
            ""
        )


        if not authorization.startswith(
            "Bearer "
        ):

            return jsonify({

                "error":
                "Department authentication required"

            }), 401


        token = authorization.replace(
            "Bearer ",
            "",
            1
        )


        if token not in department_tokens:

            return jsonify({

                "error":
                "Invalid or expired department token"

            }), 401


        return function(
            *args,
            **kwargs
        )


    return wrapper


# =========================================================
# PRIORITY CALCULATION
# =========================================================

def calculate_priority(
    problem_type,
    description
):

    high_priority = {

        "Road Accident Hazard",
        "Blocked Drain",
        "Water Leakage"

    }


    medium_priority = {

        "Pothole",
        "Damaged Road",
        "Broken Streetlight"

    }


    if problem_type in high_priority:

        return 90


    if problem_type in medium_priority:

        return 70


    if len(description) > 200:

        return 60


    return 50


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status": "ok",

        "message":
        "NagarDrishti API is running"

    })


# =========================================================
# CITIZEN REGISTRATION
# =========================================================

@app.route(
    "/api/register",
    methods=["POST"]
)
def register():

    data = request.get_json(
        silent=True
    ) or {}


    name = data.get(
        "name",
        ""
    ).strip()


    email = data.get(
        "email",
        ""
    ).strip().lower()


    password = data.get(
        "password",
        ""
    )


    # Validation

    if not name:

        return jsonify({

            "error":
            "Name is required"

        }), 400


    if not email:

        return jsonify({

            "error":
            "Email is required"

        }), 400


    if not password:

        return jsonify({

            "error":
            "Password is required"

        }), 400


    if len(password) < 6:

        return jsonify({

            "error":
            "Password must contain at least 6 characters"

        }), 400


    connection = get_db()


    try:

        password_hash = generate_password_hash(
            password
        )


        connection.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash,
                created_at
            )

            VALUES (?, ?, ?, ?)
            """,

            (
                name,
                email,
                password_hash,
                datetime.now().isoformat()
            )
        )


        connection.commit()


    except sqlite3.IntegrityError:

        connection.close()


        return jsonify({

            "error":
            "Email already registered"

        }), 409


    connection.close()


    return jsonify({

        "message":
        "Registration successful"

    }), 201


# =========================================================
# CITIZEN LOGIN
# =========================================================

@app.route(
    "/api/login",
    methods=["POST"]
)
def login():

    data = request.get_json(
        silent=True
    ) or {}


    email = data.get(
        "email",
        ""
    ).strip().lower()


    password = data.get(
        "password",
        ""
    )


    connection = get_db()


    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,

        (email,)
    ).fetchone()


    connection.close()


    if not user:

        return jsonify({

            "error":
            "Invalid email or password"

        }), 401


    if not check_password_hash(
        user["password_hash"],
        password
    ):

        return jsonify({

            "error":
            "Invalid email or password"

        }), 401


    token = generate_token(
        "citizen"
    )


    citizen_tokens[token] = user["id"]


    return jsonify({

        "message":
        "Login successful",

        "token":
        token,

        "user": {

            "id":
            user["id"],

            "name":
            user["name"],

            "email":
            user["email"]

        }

    })


# =========================================================
# DEPARTMENT LOGIN
# =========================================================

@app.route(
    "/api/department/login",
    methods=["POST"]
)
def department_login():

    data = request.get_json(
        silent=True
    ) or {}


    email = data.get(
        "email",
        ""
    ).strip().lower()


    password = data.get(
        "password",
        ""
    )


    if email != DEPARTMENT_EMAIL:

        return jsonify({

            "error":
            "Invalid department credentials"

        }), 401


    if not check_password_hash(
        DEPARTMENT_PASSWORD_HASH,
        password
    ):

        return jsonify({

            "error":
            "Invalid department credentials"

        }), 401


    token = generate_token(
        "department"
    )


    department_tokens.add(
        token
    )


    return jsonify({

        "message":
        "Department login successful",

        "token":
        token,

        "department":
        "Civic Department"

    })


# =========================================================
# CREATE CIVIC REPORT
# =========================================================

@app.route(
    "/api/reports",
    methods=["POST"]
)
@citizen_required
def create_report():

    problem_type = request.form.get(
        "problem_type",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    location = request.form.get(
        "location",
        ""
    ).strip()


    latitude = request.form.get(
        "latitude",
        ""
    )


    longitude = request.form.get(
        "longitude",
        ""
    )


    contact = request.form.get(
        "contact",
        ""
    ).strip()


    image = request.files.get(
        "image"
    )


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not problem_type:

        return jsonify({

            "error":
            "Problem type is required"

        }), 400


    if not description:

        return jsonify({

            "error":
            "Problem description is required"

        }), 400


    # -----------------------------------------------------
    # GET CITIZEN
    # -----------------------------------------------------

    connection = get_db()


    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,

        (request.user_id,)
    ).fetchone()


    if not user:

        connection.close()


        return jsonify({

            "error":
            "Citizen account not found"

        }), 404


    # -----------------------------------------------------
    # GENERATE TRACKING ID
    # -----------------------------------------------------

    tracking_id = (

        "NGR-"

        + datetime.now().strftime(
            "%Y%m%d"
        )

        + "-"

        + secrets.token_hex(
            3
        ).upper()

    )


    # -----------------------------------------------------
    # IMAGE UPLOAD
    # -----------------------------------------------------

    image_path = None


    if image and image.filename:

        original_name = os.path.basename(
            image.filename
        )


        filename = (

            secrets.token_hex(
                8
            )

            + "_"

            + original_name

        )


        save_path = os.path.join(

            UPLOAD_FOLDER,

            filename

        )


        image.save(
            save_path
        )


        image_path = (

            "/api/uploads/"
            + filename

        )


    # -----------------------------------------------------
    # LATITUDE / LONGITUDE
    # -----------------------------------------------------

    try:

        latitude_value = (
            float(latitude)
            if latitude
            else None
        )

    except ValueError:

        latitude_value = None


    try:

        longitude_value = (
            float(longitude)
            if longitude
            else None
        )

    except ValueError:

        longitude_value = None


    # -----------------------------------------------------
    # PRIORITY
    # -----------------------------------------------------

    priority_score = calculate_priority(

        problem_type,

        description

    )


    # -----------------------------------------------------
    # TIME
    # -----------------------------------------------------

    current_time = (
        datetime.now().isoformat()
    )


    # -----------------------------------------------------
    # SAVE REPORT
    # -----------------------------------------------------

    connection.execute(
        """
        INSERT INTO reports
        (

            tracking_id,

            citizen_id,

            citizen_name,

            contact,

            problem_type,

            description,

            location,

            latitude,

            longitude,

            image_path,

            priority_score,

            status,

            assigned_department,

            created_at,

            updated_at

        )

        VALUES
        (
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?
        )
        """,

        (

            tracking_id,

            user["id"],

            user["name"],

            contact,

            problem_type,

            description,

            location,

            latitude_value,

            longitude_value,

            image_path,

            priority_score,

            "Pending",

            None,

            current_time,

            current_time

        )
    )


    connection.commit()


    report_id = (
        connection
        .execute(
            "SELECT last_insert_rowid()"
        )
        .fetchone()[0]
    )


    connection.close()


    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "message":
        "Complaint registered successfully",

        "tracking_id":
        tracking_id,

        "report_id":
        report_id,

        "status":
        "Pending",

        "priority_score":
        priority_score

    }), 201


# =========================================================
# CITIZEN'S REPORTS
# =========================================================

@app.route(
    "/api/reports/mine",
    methods=["GET"]
)
@citizen_required
def my_reports():

    connection = get_db()


    reports = connection.execute(
        """
        SELECT *
        FROM reports
        WHERE citizen_id = ?

        ORDER BY id DESC
        """,

        (request.user_id,)
    ).fetchall()


    connection.close()


    return jsonify([

        dict(report)

        for report in reports

    ])


# =========================================================
# TRACK COMPLAINT
# =========================================================

@app.route(
    "/api/reports/track/<tracking_id>",
    methods=["GET"]
)
def track_report(
    tracking_id
):

    connection = get_db()


    report = connection.execute(
        """
        SELECT *
        FROM reports

        WHERE tracking_id = ?
        """,

        (tracking_id,)
    ).fetchone()


    connection.close()


    if not report:

        return jsonify({

            "error":
            "Tracking ID not found"

        }), 404


    result = dict(report)


    # Don't expose internal citizen ID

    result.pop(
        "citizen_id",
        None
    )


    # Don't expose contact publicly

    result.pop(
        "contact",
        None
    )


    return jsonify(
        result
    )


# =========================================================
# DEPARTMENT - GET ALL REPORTS
# =========================================================

@app.route(
    "/api/department/reports",
    methods=["GET"]
)
@department_required
def department_reports():

    connection = get_db()


    reports = connection.execute(
        """
        SELECT *
        FROM reports

        ORDER BY
            priority_score DESC,
            id DESC
        """
    ).fetchall()


    connection.close()


    return jsonify([

        dict(report)

        for report in reports

    ])


# =========================================================
# DEPARTMENT - UPDATE REPORT
# =========================================================

@app.route(
    "/api/department/reports/<int:report_id>",
    methods=["PATCH"]
)
@department_required
def update_report(
    report_id
):

    data = request.get_json(
        silent=True
    ) or {}


    status = data.get(
        "status"
    )


    assigned_department = data.get(
        "assigned_department"
    )


    allowed_statuses = {

        "Pending",

        "Assigned",

        "In Progress",

        "Resolved"

    }


    if status not in allowed_statuses:

        return jsonify({

            "error":
            "Invalid complaint status"

        }), 400


    connection = get_db()


    cursor = connection.execute(
        """
        UPDATE reports

        SET

            status = ?,

            assigned_department = ?,

            updated_at = ?

        WHERE id = ?
        """,

        (

            status,

            assigned_department,

            datetime.now().isoformat(),

            report_id

        )
    )


    connection.commit()


    connection.close()


    if cursor.rowcount == 0:

        return jsonify({

            "error":
            "Complaint not found"

        }), 404


    return jsonify({

        "message":
        "Complaint updated successfully",

        "status":
        status

    })


# =========================================================
# SERVE UPLOADED IMAGES
# =========================================================

@app.route(
    "/api/uploads/<path:filename>",
    methods=["GET"]
)
def uploaded_file(
    filename
):

    return send_from_directory(

        UPLOAD_FOLDER,

        filename

    )


# =========================================================
# LOGOUT - CITIZEN
# =========================================================

@app.route(
    "/api/logout",
    methods=["POST"]
)
@citizen_required
def citizen_logout():

    authorization = request.headers.get(
        "Authorization",
        ""
    )


    token = authorization.replace(
        "Bearer ",
        "",
        1
    )


    citizen_tokens.pop(
        token,
        None
    )


    return jsonify({

        "message":
        "Citizen logged out"

    })


# =========================================================
# LOGOUT - DEPARTMENT
# =========================================================

@app.route(
    "/api/department/logout",
    methods=["POST"]
)
@department_required
def department_logout():

    authorization = request.headers.get(
        "Authorization",
        ""
    )


    token = authorization.replace(
        "Bearer ",
        "",
        1
    )


    department_tokens.discard(
        token
    )


    return jsonify({

        "message":
        "Department logged out"

    })


# =========================================================
# START APPLICATION
# =========================================================

initialize_database()


if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )
