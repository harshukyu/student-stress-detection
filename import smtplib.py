import smtplib
from email.mime.text import MIMEText

GMAIL = "harshgangwar902@gmail.com"      
PASS = "nocp dgav gyld zigk"

msg = MIMEText("CampusMind test email - working!")
msg["Subject"] = "CampusMind Test"
msg["From"] = GMAIL
msg["To"] = GMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(GMAIL, PASS)
    s.sendmail(GMAIL, GMAIL, msg.as_string())

print("Email sent successfully!")