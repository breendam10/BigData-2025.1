# app/controllers/credit_card_controller.py
from flask_restx import Namespace, Resource, fields
from flask import request
from datetime import datetime
from app.db.mysql_db import db
from app.models.credit_card_model import CreditCard
import uuid

credit_card_ns = Namespace("credit_card", description="Operações relacionadas a cartões de crédito do usuário")

credit_card_model = credit_card_ns.model("CreditCardModel", {
    "numero": fields.Integer(required=True, description="Número do cartão de crédito", example=123123412341234),
    "dtExpiracao": fields.String(required=True, description="Data de expiração em formato (dd/mm/yyyy)", example="31/12/1990"),
    "cvv": fields.String(required=True, description="Código de segurança do cartão"),
    "saldo": fields.Float(required=True, description="Saldo inicial disponível no cartão")
})

authorize_purchase_model = credit_card_ns.model("AuthorizePurchaseRequest", {
    "valor": fields.Float(required=True, description="Valor da compra a ser autorizado", example=99.90)
})

authorize_response_model = credit_card_ns.model("AuthorizePurchaseResponse", {
    "status": fields.String(example="AUTHORIZED"),
    "message": fields.String(example="Cartão autorizado"),
    "saldo": fields.Float(required=True, example=100.00)
})

@credit_card_ns.route("/<int:user_id>")
class CreditCardList(Resource):
    @credit_card_ns.expect(credit_card_model, validate=True)
    @credit_card_ns.response(201, "Cartão criado com sucesso")
    @credit_card_ns.response(400, "Erro ao criar cartão de crédito")
    def post(self, user_id):
        """Cadastra cartão para um usuário."""
        data = credit_card_ns.payload
        try:
            numero = data["numero"]
            cvv = data["cvv"]
            saldo = data["saldo"]
            dt_str = data["dtExpiracao"]
            dt_exp = None

            try:
                numero_int = int(numero)
            except ValueError:
                return {"error": "Número do cartão deve ser um inteiro numérico."}, 400

            if len(str(numero_int)) < 13 or len(str(numero_int)) > 16:
                return {"error": "Número do cartão deve ter entre 13 e 16 dígitos."}, 400

            exists = CreditCard.query.filter_by(user_id=user_id, numero=numero_int).first()
            if exists:
                return {"error": "Esse usuário já possui um cartão com esse número."}, 400

            if dt_str:
                try:
                    dt_exp = datetime.strptime(dt_str, "%d/%m/%Y").date()
                except ValueError:
                    return {"error": "Formato de data inválido. Use dd/mm/yyyy."}, 400

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

    @credit_card_ns.response(200, "Lista de cartões retornada com sucesso")
    def get(self, user_id):
        """
        Retorna todos os cartões de crédito de um usuário.
        """
        cards = CreditCard.query.filter_by(user_id=user_id).all()
        return {
            "cartoes": [card.to_dict() for card in cards]
        }, 200

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

@credit_card_ns.route("/<int:user_id>/<int:card_id>/authorize")
class CreditCardAuthorize(Resource):
    @credit_card_ns.expect(authorize_purchase_model, validate=True)
    @credit_card_ns.response(200, "Cartão autorizado", authorize_response_model)
    @credit_card_ns.response(400, "Cartão não autorizado", authorize_response_model)
    @credit_card_ns.response(404, "Cartão não encontrado", authorize_response_model)
    def post(self, user_id, card_id):
        """
        Autoriza uma transação de compra em um cartão de crédito do usuário.
        """
        data = request.json
        valor = data.get("valor")

        # Busca cartão do usuário
        card = CreditCard.query.filter_by(id=card_id, user_id=user_id).first()
        if not card:
            return {
                "status": "NOT_AUTHORIZED",
                "message": "Cartão não encontrado para o usuário",
                "saldo": 0
            }, 404

        # Verifica validade
        if card.dtExpiracao < datetime.now().date():
            return {
                "status": "NOT_AUTHORIZED",
                "message": "Cartão expirado",
                "saldo": card.saldo
            }, 400

        # Verifica saldo suficiente
        if card.saldo < valor:
            return {
                "status": "NOT_AUTHORIZED",
                "message": "Saldo insuficiente",
                "saldo": card.saldo
            }, 400

        # Cartão autorizado
        return {
            "status": "AUTHORIZED",
            "message": "Cartão autorizado",
            "saldo": card.saldo
        }, 200
