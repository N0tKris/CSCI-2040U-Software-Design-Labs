from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os

app = Flask(__name__)
app.secret_key = "draft_secret_key"  # Needed for flash messages

# Backend URL (change if your backend runs on a different port/host)
BACKEND_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8080")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        # Validate input
        if not username or not password:
            flash("Username and password are required!", "error")
            return redirect(url_for("register"))

        # Send registration request to Spring Boot backend
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/users",
                json={"username": username, "password": password, "role": "USER"},
                timeout=5
            )

            if response.status_code == 201:
                flash("Account created successfully!", "success")
            elif response.status_code == 409:
                flash("Username already exists!", "error")
            else:
                flash("Failed to create account. Try again.", "error")

        except requests.exceptions.RequestException as e:
            flash(f"Error connecting to backend: {str(e)}", "error")

        return redirect(url_for("register"))

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)