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
