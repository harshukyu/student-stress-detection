from flask import Flask, render_template, request

app = Flask(__name__)


# Home page
@app.route('/')
def home():
    return render_template("index.html")


# Register page
@app.route('/register')
def register():
    return render_template("register.html")


# Form submission (just redirects to dashboard)
@app.route('/predict', methods=['POST'])
def predict():
    return render_template("dashboard.html")


# Dashboard page
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)