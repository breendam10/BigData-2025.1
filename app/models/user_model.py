# app/models/user_model.py
from app.db.mysql_db import db
import datetime

class User(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    dtNascimento = db.Column(db.Date, nullable=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)

    addresses = db.relationship('Address', backref='user', lazy=True)
    credit_cards = db.relationship('CreditCard', backref='user', lazy=True)

    def __init__(self, nome, email, dtNascimento, cpf, telefone):
        self.nome = nome
        self.email = email
        self.dtNascimento = dtNascimento
        self.cpf = cpf
        self.telefone = telefone

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "dtNascimento": self.dtNascimento.strftime("%d/%m/%Y") if self.dtNascimento else None,
            "cpf": self.cpf,
            "telefone": self.telefone
        }
