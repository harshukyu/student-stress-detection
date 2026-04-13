from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, hashlib, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = "campusmind_secret_2024"

DB = "campusmind.db"

# =============================================
# Gmail setup
# =============================================
GMAIL_ADDRESS  = "your_email@gmail.com"   
GMAIL_APP_PASS = "xxxx xxxx xxxx xxxx"    
# =============================================

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

import pickle
import numpy as np

with open("stress_model.pkl", "rb") as f:
    ml_model = pickle.load(f)

def predict_stress(sleep, study, screen, mood):
    sleep_quality = min(int(sleep * 9 / 24), 9)
    study_load    = min(int(study), 9)
    anxiety_level = max(0, int((5 - mood) * 5))
    mental_health = 1 if mood <= 2 else 0
    features = np.array([[sleep_quality, study_load, anxiety_level, mental_health]])
    prediction = ml_model.predict(features)[0]
    mapping = {0: "Low", 1: "Moderate", 2: "High"}
    return mapping[int(prediction)]
    
def send_stress_alert(to_email, username, sleep, study, screen, mood):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🚨 CampusMind High Stress Alert"
        msg["From"]    = GMAIL_ADDRESS
        msg["To"]      = to_email

        html = f"""
        <html><body style="font-family:sans-serif;background:#0f1f3d;color:#fff;padding:32px;">
          <div style="max-width:520px;margin:auto;background:#162847;border-radius:16px;padding:32px;">
            <h2 style="color:#c9a84c;font-size:22px;">🧠 CampusMind Alert</h2>
            <p style="font-size:16px;margin:16px 0;">Hi <strong>{username}</strong>,</p>
            <p style="color:#8a9ab5;">Your latest stress assessment shows <strong style="color:#e05c5c;">HIGH STRESS</strong>. Please take immediate action.</p>
            <div style="background:#1e3a5f;border-radius:10px;padding:20px;margin:20px 0;">
              <p style="margin:6px 0;">😴 Sleep: <strong>{sleep} hrs</strong></p>
              <p style="margin:6px 0;">📚 Study: <strong>{study} hrs</strong></p>
              <p style="margin:6px 0;">📱 Screen Time: <strong>{screen} hrs</strong></p>
              <p style="margin:6px 0;">😊 Mood: <strong>{mood}/5</strong></p>
            </div>
            <p style="color:#8a9ab5;font-size:14px;"><strong style="color:#fff;">Tips to reduce stress:</strong><br>
            ✅ Sleep 7–9 hours tonight<br>
            ✅ Meditate for 10 minutes<br>
            ✅ Reduce screen time below 4 hours<br>
            ✅ Take a 30-min walk<br>
            ✅ Talk to a friend or counsellor</p>
            <p style="margin-top:24px;font-size:12px;color:#8a9ab5;">— CampusMind Wellness Platform</p>
          </div>
        </body></html>
        """
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect(url_for('home'))
        except:
            return render_template("register.html", error="Username already exists.")
    return render_template("register.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = hashlib.sha256(request.form['password'].encode()).hexdigest()
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    if user:
        session['user_id']  = user['id']
        session['username'] = user['username']
        return redirect(url_for('dashboard'))
    return render_template("index.html", error="Invalid username or password.")

@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    sleep  = float(request.form['sleep'])
    study  = float(request.form['study'])
    screen = float(request.form['screen'])
    mood   = int(request.form['mood'])
    email  = request.form.get('email', '').strip()
    stress = predict_stress(sleep, study, screen, mood)

    db = get_db()
    db.execute(
        "INSERT INTO stress_data (user_id, sleep, study, screen, mood, stress_level) VALUES (?,?,?,?,?,?)",
        (session['user_id'], sleep, study, screen, mood, stress)
    )
    db.commit()

    history = db.execute(
        "SELECT * FROM stress_data WHERE user_id=? ORDER BY id DESC LIMIT 10",
        (session['user_id'],)
    ).fetchall()

    email_sent = None
    if stress == "High" and email:
        success = send_stress_alert(email, session['username'], sleep, study, screen, mood)
        if success:
            email_sent = email

    return render_template("dashboard.html",
        stress=stress, sleep=sleep, study=study, screen=screen,
        mood=mood, username=session['username'],
        history=history, email_sent=email_sent
    )

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    db = get_db()
    history = db.execute(
        "SELECT * FROM stress_data WHERE user_id=? ORDER BY id DESC LIMIT 10",
        (session['user_id'],)
    ).fetchall()
    return render_template("dashboard.html", history=history, username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
