import os
import sqlite3
import uuid

from flask import (
    Flask,
    flash,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)
from datetime import timedelta

app.permanent_session_lifetime = timedelta(days=30)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "samchat.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "profile_pics")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with get_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                profile_pic TEXT
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
init_db()

def save_profile_picture(file):
    if not file or not file.filename:
        return None

    filename = secure_filename(file.filename)

    if "." not in filename:
        raise ValueError("Invalid image file.")

    extension = filename.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PNG, JPG, JPEG or WEBP allowed.")

    new_filename = f"{uuid.uuid4().hex}.{extension}"
    file.save(os.path.join(UPLOAD_FOLDER, new_filename))

    return new_filename


HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <meta name="google-site-verification" content="Vvki8wlgWm1nkru8ON8cbG1-y7sBmfc0lFkguPL488Y" />

    <title>Xter</title>
<link rel="icon" type="image/jpeg" href="{{ url_for('static', filename='xsam.jpg.jpg') }}">
    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #14002c, #4b0082);
            color: white;
        }

        .container {
            max-width: 750px;
            margin: auto;
        }

        .card {
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.1);
        }

        input {
            padding: 12px;
            margin: 5px;
            border: none;
            border-radius: 10px;
        }

        button {
            padding: 12px;
            margin: 5px;
            border: none;
            border-radius: 10px;
            background: #9f5cff;
            color: white;
            cursor: pointer;
        }

        button:hover {
            background: #7c3aed;
        }

        .profile {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }

        .avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            object-fit: cover;
            background: #9f5cff;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            font-weight: bold;
        }

        .chat {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            height: 400px;
            overflow-y: auto;
            padding: 15px;
            margin-bottom: 10px;
        }

        .message {
            display: flex;
            gap: 10px;
            align-items: flex-start;
            margin-bottom: 12px;
        }

        .bubble {
            flex: 1;
            padding: 10px;
            border-radius: 12px;
            background: #7c3aed;
            overflow-wrap: anywhere;
        }

        .bubble small {
            display: block;
            margin-top: 6px;
            opacity: 0.7;
        }

        .message-input {
            width: calc(100% - 90px);
        }

        .flash {
            padding: 12px;
            border-radius: 10px;
            background: #ef4444;
        }

        .success {
            background: #16a34a;
        }

        a {
            color: white;
            text-decoration: none;
        }
    </style>
</head>

<body>
<div class="container">

    {% for category, message in get_flashed_messages(with_categories=true) %}
        <p class="flash {{ category }}">{{ message }}</p>
    {% endfor %}

    {% if not session.get("user_id") %}

        <div class="card">
            <h2>Register</h2>

            <form action="{{ url_for('register') }}" method="post">
                <input
                    name="username"
                    placeholder="Username"
                    minlength="3"
                    maxlength="30"
                    required
                >

                <input
                    name="password"
                    type="password"
                    placeholder="Password"
                    minlength="6"
                    required
                >

                <button type="submit">Register</button>
            </form>
        </div>

        <div class="card">
            <h2>Login</h2>

            <form action="{{ url_for('login') }}" method="post">
                <input
                    name="username"
                    placeholder="Username"
                    required
                >

                <input
                    name="password"
                    type="password"
                    placeholder="Password"
                    required
                >

                <button type="submit">Login</button>
            </form>
        </div>

    {% else %}

        <div class="profile">

            {% if current_user.profile_pic %}
                <img
                    class="avatar"
                    src="{{ url_for(
                        'static',
                        filename='profile_pics/' + current_user.profile_pic
                    ) }}"
                    alt="Profile picture"
                >
            {% else %}
<span class="avatar">
    {% if current_user %}
        {{ current_user.username[0]|upper }}
    {% else %}
        U
    {% endif %}
</span>
{% endif %}
            {% if current_user %}
<h2>Welcome {{ current_user.username }}</h2>
{% endif %}

            <a href="{{ url_for('logout') }}">
                <button>Logout</button>
            </a>
        </div>

        <div class="card">
            <h3>
                {% if current_user.profile_pic %}
                    Change Profile Picture
                {% else %}
                    Add Profile Picture
                {% endif %}
            </h3>

            <form
                action="{{ url_for('update_profile_picture') }}"
                method="post"
                enctype="multipart/form-data"
            >
                <input
                    name="profile_pic"
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    required
                >

                <button type="submit">Update Photo</button>
            </form>

            <small>PNG, JPG or WEBP. Maximum size 2 MB.</small>
        </div>

        <div class="chat" id="chat">

            {% for msg in messages %}

                <div class="message">

                    {% if msg.profile_pic %}
                        <img
                            class="avatar"
                            src="{{ url_for(
                                'static',
                                filename='profile_pics/' + msg.profile_pic
                            ) }}"
                            alt="Profile picture"
                        >
                    {% else %}
                        <span class="avatar">
                            {{ msg.username[0]|upper }}
                        </span>
                    {% endif %}

                    <div class="bubble">
                        <b>{{ msg.username }}</b>: {{ msg.text }}
                        <small>{{ msg.created_at }}</small>
                    </div>

                </div>

            {% else %}

                <p>No messages yet.</p>

            {% endfor %}

        </div>

        <form action="{{ url_for('send') }}" method="post">
            <input
                class="message-input"
                name="message"
                placeholder="Type a message..."
                maxlength="500"
                required
            >

            <button type="submit">Send</button>
        </form>

        <script>
            const chat = document.getElementById("chat");
            chat.scrollTop = chat.scrollHeight;
        </script>

    {% endif %}

</div>
</body>
</html>
"""


@app.route("/")
def home():
    current_user = None
    messages = []

    if session.get("user_id"):
        with get_db() as db:
            current_user = db.execute(
                "SELECT * FROM users WHERE id = ?",
                (session["user_id"],),
            ).fetchone()

            messages = db.execute(        
                """
                SELECT
                    messages.text,
                    messages.created_at,
                    users.username,
                    users.profile_pic
                FROM messages
                JOIN users ON users.id = messages.user_id
                ORDER BY messages.id ASC
                """
            ).fetchall()

    return render_template_string(
        HTML,
        current_user=current_user,
        messages=messages,
    )


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if len(username) < 3 or len(password) < 6:
        flash("Username minimum 3 and password minimum 6 characters.")
        return redirect(url_for("home"))

    try:
        with get_db() as db:
            db.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
                """,
                (username, generate_password_hash(password)),
            )
            db.commit()

        flash("Registration successful. Now login.", "success")

    except sqlite3.IntegrityError:
        flash("Username already registered.")

    return redirect(url_for("home"))


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    with get_db() as db:
        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if user and check_password_hash(user["password_hash"], password):
        session.clear()
        session["user_id"] = user["id"]
        session.permanent = True
    else:
        flash("Wrong username or password.")

    return redirect(url_for("home"))


@app.route("/profile-picture", methods=["POST"])
def update_profile_picture():
    if not session.get("user_id"):
        flash("Please login first.")
        return redirect(url_for("home"))

    try:
        new_picture = save_profile_picture(
            request.files.get("profile_pic")
        )

        if not new_picture:
            raise ValueError("Please select an image.")

        with get_db() as db:
            old_user = db.execute(
                "SELECT profile_pic FROM users WHERE id = ?",
                (session["user_id"],),
            ).fetchone()

            db.execute(
                "UPDATE users SET profile_pic = ? WHERE id = ?",
                (new_picture, session["user_id"]),
            )

        if old_user and old_user["profile_pic"]:
            old_picture = os.path.join(
                UPLOAD_FOLDER,
                old_user["profile_pic"],
            )

            if os.path.isfile(old_picture):
                os.remove(old_picture)

        flash("Profile picture updated.", "success")

    except ValueError as error:
        flash(str(error))

    return redirect(url_for("home"))


@app.route("/send", methods=["POST"])
def send():
    if not session.get("user_id"):
        flash("Please login first.")
        return redirect(url_for("home"))

    message = request.form.get("message", "").strip()

    if message:
        with get_db() as db:
            db.execute(
                """
                INSERT INTO messages (user_id, text)
                VALUES (?, ?)
                """,
                (session["user_id"], message[:500]),
            )
            db.commit()

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.errorhandler(413)
def file_too_large(error):
    flash("Profile picture must be smaller than 2 MB.")
    return redirect(url_for("home"))
if __name__ == "__main__":
    app.run(debug=True)
