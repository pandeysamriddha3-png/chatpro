 
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
    font-family:Arial;
    background:#1e1e1e;
    color:white;
    padding:20px;
}
input,button{
    padding:8px;
    margin:5px;
}
.chat{
    border:1px solid #555;
    height:300px;
    overflow-y:auto;
    padding:10px;
    margin-bottom:10px;
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
<p><b>{{msg.user}}</b>: {{msg.text}}</p>
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
