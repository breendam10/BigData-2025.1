# app/models/address_model.py
from app.db.mysql_db import db

class Address(db.Model):
    __tablename__ = "enderecos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    logradouro = db.Column(db.String(255), nullable=False)
    complemento = db.Column(db.String(255), nullable=True)
    bairro = db.Column(db.String(255), nullable=True)
    cidade = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(255), nullable=False)
    cep = db.Column(db.String(20), nullable=False)

    def __init__(self, user_id, logradouro, complemento, bairro, cidade, estado, cep):
        self.user_id = user_id
        self.logradouro = logradouro
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.cep = cep

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "logradouro": self.logradouro,
            "complemento": self.complemento,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "estado": self.estado,
            "cep": self.cep
        }
