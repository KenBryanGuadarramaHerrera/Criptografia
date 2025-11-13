from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False) # En prod: usar HASH
    # Guardamos la llave pública del usuario como registro
    public_key_pem = db.Column(db.Text, nullable=False)
    # CRÍTICO: Bandera para asegurar un solo voto
    has_voted = db.Column(db.Boolean, default=False)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vote_content = db.Column(db.String(100), nullable=False)
    signature = db.Column(db.String(1000), nullable=False) # Firma RSA del Admin