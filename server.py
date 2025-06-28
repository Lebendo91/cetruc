import smtplib
from email.message import EmailMessage
from flask import Flask, request, jsonify, render_template_string, redirect
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
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
    <body style='font-family:sans-serif;'>
        <h2>Réservation confirmée</h2>
        <p>Bonjour <strong>{reservation['name']}</strong>,</p>
        <p>Merci pour votre réservation du véhicule <strong>{reservation['carName']}</strong>.</p>
        <ul>
            <li>Du : {reservation['startDate']}</li>
            <li>Au : {reservation['endDate']}</li>
            <li>Paiement : {reservation['paymentMethod']}</li>
        </ul>
        <p>Un conseiller LuxDrive vous contactera prochainement.</p>
        <hr>
        <small>Ceci est un message automatique de LuxDrive.</small>
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
        <h1>Réservation confirmée</h1>
        <p>Merci pour votre confiance. Un conseiller LuxDrive vous contactera sous peu.</p>
        <a href="/">Retour à l'accueil</a>
    """)

@app.route('/success')
def success():
    return redirect("/confirmation")

@app.route('/cancel')
def cancel():
    return "<h1>Paiement annulé</h1><p>La transaction a été interrompue.</p>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)