import smtplib
from email.message import EmailMessage
from flask import Flask, request, jsonify, render_template_string, redirect
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

RES_FILE = 'reservations.json'

def send_confirmation_email(to_email, reservation):
    with open("config.json") as f:
        cfg = json.load(f)

    msg = EmailMessage()
    msg["Subject"] = "Confirmation de votre réservation - LuxDrive"
    msg["From"] = f"{cfg['FROM_NAME']} <{cfg['FROM_EMAIL']}>"
    msg["To"] = to_email

    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f8f8f8; padding: 30px;">
        <div style="max-width: 600px; margin: auto; background-color: #fff; border-radius: 10px; padding: 30px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
          <h2 style="color: #222;">✨ Réservation confirmée</h2>
          <p>Bonjour <strong>{reservation['name']}</strong>,</p>
          <p>Merci d'avoir réservé le véhicule <strong>{reservation['carName']}</strong> sur <span style="color: #000;">LuxDrive</span>.</p>
          <ul style="list-style: none; padding: 0;">
            <li><strong>🗓 Du :</strong> {reservation['startDate']}</li>
            <li><strong>🗓 Au :</strong> {reservation['endDate']}</li>
            <li><strong>💳 Paiement :</strong> {reservation['paymentMethod']}</li>
          </ul>
          <p style="margin-top: 20px;">Un conseiller vous contactera prochainement.</p>
          <hr style="margin-top: 30px; border: none; border-top: 1px solid #eee;">
          <p style="font-size: 12px; color: #777;">Ce message vous est envoyé automatiquement par LuxDrive.</p>
        </div>
      </body>
    </html>
    """
    msg.set_content("Confirmation de réservation")
    msg.add_alternative(body, subtype='html')

    with smtplib.SMTP(cfg['SMTP_HOST'], cfg['SMTP_PORT']) as smtp:
        smtp.starttls()
        smtp.login(cfg['SMTP_USER'], cfg['SMTP_PASSWORD'])
        smtp.send_message(msg)

@app.route('/')
def home():
    return app.send_static_file("index.html")

@app.route('/reserve', methods=['POST'])
def reserve():
    data = request.json
    data['timestamp'] = datetime.now().isoformat()
    if not os.path.exists(RES_FILE):
        with open(RES_FILE, 'w') as f:
            json.dump([], f)

    with open(RES_FILE, 'r+') as f:
        reservations = json.load(f)
        reservations.append(data)
        f.seek(0)
        json.dump(reservations, f, indent=2)

    try:
        send_confirmation_email(data.get("email"), data)
    except Exception as e:
        print("Erreur envoi mail:", e)

    return jsonify({"status": "ok"})

@app.route('/confirmation')
def confirmation():
    return render_template_string("""
        <html>
        <head><meta charset="UTF-8"><title>Confirmation</title></head>
        <body style="font-family:sans-serif; background:#f6f6f6; text-align:center; padding:50px;">
          <div style="background:white; display:inline-block; padding:40px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1);">
            <h1 style="color:#333;">✅ Réservation confirmée</h1>
            <p style="font-size:18px;">Merci pour votre confiance. Un conseiller LuxDrive vous contactera sous peu.</p>
            <a href="https://lebendo91.github.io/luuxe/#" style="display:inline-block; margin-top:20px; background:#000; color:white; padding:12px 24px; border-radius:6px; text-decoration:none;">Retour à l'accueil</a>
          </div>
        </body>
        </html>
    """)

@app.route('/success')
def success():
    return redirect("/confirmation")

@app.route('/cancel')
def cancel():
    return "<h1>Paiement annulé</h1><p>La transaction a été interrompue.</p>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
