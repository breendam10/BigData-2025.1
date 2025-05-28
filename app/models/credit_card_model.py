# app/models/credit_card_model.py
from app.db.mysql_db import db

class CreditCard(db.Model):
    __tablename__ = "cartoes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    numero = db.Column(db.String(16), nullable=False)
    dtExpiracao = db.Column(db.Date, nullable=False)
    cvv = db.Column(db.String(3), nullable=False)
    saldo = db.Column(db.Float, default=0)

    def __init__(self, user_id, numero, dtExpiracao, cvv, saldo):
        self.user_id = user_id
        self.numero = numero
        self.dtExpiracao = dtExpiracao
        self.cvv = cvv
        self.saldo = saldo

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "numero": self.numero,
            "dtExpiracao": self.dtExpiracao.strftime("%d/%m/%Y") if self.dtExpiracao else None,
            "cvv": self.cvv,
            "saldo": self.saldo
        }
