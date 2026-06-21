from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = "mysecretkey"

users = {}
messages = []

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini Chat</title>
    <style>
        body{
            margin:0;
            padding:20px;
            font-family:Arial,sans-serif;
            background:linear-gradient(135deg,#14002c,#4b0082);
            color:white;
        }

        input{
            padding:12px;
            margin:5px;
            border:none;
            border-radius:10px;
        }

        button{
            padding:12px;
            margin:5px;
            border:none;
            border-radius:10px;
            background:#9f5cff;
            color:white;
            cursor:pointer;
        }

        .chat{
            background:rgba(255,255,255,0.1);
            border-radius:20px;
            height:400px;
            overflow-y:auto;
            padding:15px;
            margin-bottom:10px;
        }

        .chat p{
            background:#7c3aed;
            padding:10px;
            border-radius:12px;
        }
    </style>
</head>
<body>

{% if not session.get('user') %}

    <h2>Register</h2>
    <form action="/register" method="post">
        <input name="username" placeholder="Username" required>
        <input name="password" type="password" placeholder="Password" required>
        <button type="submit">Register</button>
    </form>

    <h2>Login</h2>
    <form action="/login" method="post">
        <input name="username" placeholder="Username" required>
        <input name="password" type="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>

{% else %}

    <h2>Welcome {{ session['user'] }}</h2>

    <a href="/logout">
        <button>Logout</button>
    </a>

    <div class="chat">
        {% for msg in messages %}
            <p><b>{{ msg.user }}</b>: {{ msg.text }}</p>
        {% endfor %}
    </div>

    <form action="/send" method="post">
        <input name="message" placeholder="Type a message..." required>
        <button type="submit">Send</button>
    </form>

{% endif %}

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, messages=messages)

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    if username not in users:
        users[username] = password

    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if username in users and users[username] == password:
        session["user"] = username

    return redirect("/")

@app.route("/send", methods=["POST"])
def send():
    if "user" in session:
        messages.append({
            "user": session["user"],
            "text": request.form["message"]
        })

    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
