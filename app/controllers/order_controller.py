# C:\Users\ianes\Desktop\BigData-2025.1\app\controllers\order_controller.py

from flask_restx import Namespace, Resource, fields
from flask import request
from datetime import datetime
from app.db.mysql_db import db
from app.models.order_model import Order
from app.models.user_model import User
from app.models.credit_card_model import CreditCard
from app.db.cosmos_db import get_cosmos_container
from sqlalchemy import extract

order_ns = Namespace("orders", description="Operações de pedidos")

order_request_model = order_ns.model("OrderRequest", {
    "user_id": fields.Integer(required=True),
    "product_id": fields.String(required=True),
    "quantity": fields.Integer(required=True),
    "card_id": fields.Integer(required=True)
})

@order_ns.route("")
class OrderCreate(Resource):
    @order_ns.expect(order_request_model)
    def post(self):
        """
        Realiza uma compra.
        """
        data = request.json
        user_id = data.get("user_id")
        product_id = data.get("product_id")
        quantity = data.get("quantity")
        card_id = data.get("card_id")

        # Validações de quantidade
        if quantity is None or quantity < 1:
            return {"error": "A quantidade deve ser maior ou igual a 1"}, 400

        # Valida usuário
        user = User.query.get(user_id)
        if not user:
            return {"error": "Usuário não encontrado"}, 404

        # Valida cartão
        card = CreditCard.query.filter_by(id=card_id, user_id=user_id).first()
        if not card:
            return {"error": "Cartão não encontrado"}, 404

        # Verifica se está expirado
        if card.dtExpiracao < datetime.now().date():
            return {"error": "Cartão expirado"}, 400

        # Busca produto no CosmosDB
        container = get_cosmos_container()
        try:
            product = container.read_item(item=product_id, partition_key=product_id)
        except Exception as e:
            return {"error": "Produto não encontrado"}, 404

        price = product["price"]
        name = product["productName"]
        total = price * quantity

        # Checa saldo do cartão
        if card.saldo < total:
            return {"error": "Saldo insuficiente no cartão"}, 400

        # Debita valor do cartão
        card.saldo -= total

        # Cria pedido
        order = Order(
            user_id=user_id,
            card_id=card_id,
            product_id=product_id,
            product_name=name,
            quantity=quantity,
            total_price=total
        )
        db.session.add(order)
        db.session.commit()

        return {"message": "Pedido realizado com sucesso", "order": order.to_dict()}, 201

@order_ns.route("/extract/<int:user_id>/<int:card_id>/<int:month>")
class CardExtract(Resource):
    def get(self, user_id, card_id, month):
        """
        Extrato de compras de um cartão do usuário filtrando pelo mês.
        """
        # month deve ser de 1 a 12
        if not (1 <= month <= 12):
            return {"error": "Mês inválido. Use um número de 1 a 12."}, 400

        # Filtra por mês usando SQLAlchemy extract
        orders = Order.query.filter(
            Order.user_id == user_id,
            Order.card_id == card_id,
            extract('month', Order.dt_pedido) == month
        ).order_by(Order.dt_pedido.desc()).all()
        return {"extrato": [order.to_dict() for order in orders]}

@order_ns.route("/<int:user_id>")
class OrdersByUser(Resource):
    def get(self, user_id):
        """
        Lista todos os pedidos de um usuário.
        """
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.dt_pedido.desc()).all()
        return {"pedidos": [order.to_dict() for order in orders]}

@order_ns.route("/<int:user_id>/<int:pedido_id>")
class OrderById(Resource):
    def get(self, user_id, pedido_id):
        """
        Consulta um pedido pelo ID do usuário e do pedido.
        """
        order = Order.query.filter_by(user_id=user_id, id=pedido_id).first()
        if not order:
            return {"error": "Pedido não encontrado"}, 404
        return {"pedido": order.to_dict()}, 200
