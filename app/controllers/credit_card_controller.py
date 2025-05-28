# app/controllers/credit_card_controller.py
from flask_restx import Namespace, Resource, fields
from flask import request
from datetime import datetime
from app.db.mysql_db import db
from app.models.credit_card_model import CreditCard

credit_card_ns = Namespace("credit_card", description="Operações relacionadas a cartões de crédito do usuário")

credit_card_model = credit_card_ns.model("CreditCardModel", {
    "numero": fields.String(required=True, description="Número do cartão de crédito"),
    "dtExpiracao": fields.String(required=True, description="Data de expiração em formato (dd/mm/yyyy)", example="31/12/1990"),
    "cvv": fields.String(required=True, description="Código de segurança do cartão"),
    "saldo": fields.Float(required=True, description="Saldo inicial disponível no cartão")
})

@credit_card_ns.route("/<int:user_id>")
class CreditCardList(Resource):
    @credit_card_ns.expect(credit_card_model, validate=True)
    @credit_card_ns.response(201, "Cartão criado com sucesso")
    @credit_card_ns.response(400, "Erro ao criar cartão de crédito")
    def post(self, user_id):
        data = credit_card_ns.payload
        try:
            numero = data["numero"]
            cvv = data["cvv"]
            saldo = data["saldo"]
            dt_str = data["dtExpiracao"]
            dt_exp = None

            if dt_str:
                try:
                    dt_exp = datetime.strptime(dt_str, "%d/%m/%Y").date()
                except ValueError:
                    return {"error": "Formato de data inválido. Use dd/mm/yyyy."}, 400

            if len(numero) != 16 or not numero.isdigit():
                return {"error": "Número do cartão deve ter 16 dígitos."}, 400

            if len(cvv) != 3 or not cvv.isdigit():
                return {"error": "Número do CVV deve ter 3 dígitos."}, 400

            new_card = CreditCard(
                user_id=user_id,
                numero=numero,
                dtExpiracao=dt_exp,
                cvv=cvv,
                saldo=saldo
            )
            db.session.add(new_card)
            db.session.commit()

            return {
                "message": "Cartão criado com sucesso",
                "card": new_card.to_dict()
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

@credit_card_ns.route("/<int:user_id>/<int:card_id>")
class CreditCardResource(Resource):
    @credit_card_ns.response(200, "Sucesso")
    @credit_card_ns.response(404, "Cartão não encontrado")
    def get(self, user_id, card_id):
        """Retorna um cartão pelo ID e usuário."""
        card = CreditCard.query.filter_by(id=card_id, user_id=user_id).first()
        if not card:
            return {"error": "Cartão não encontrado"}, 404
        return {"card": card.to_dict()}, 200

    @credit_card_ns.response(204, "Cartão deletado com sucesso")
    @credit_card_ns.response(404, "Cartão não encontrado")
    def delete(self, user_id, card_id):
        """Deleta um cartão específico de um usuário."""
        card = CreditCard.query.filter_by(id=card_id, user_id=user_id).first()
        if not card:
            return {"error": "Cartão não encontrado"}, 404
        db.session.delete(card)
        db.session.commit()
        return "", 204