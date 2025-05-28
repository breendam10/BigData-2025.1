# C:\Users\ianes\Desktop\BigData-2025.1\app\models\order_model.py

from app.db.mysql_db import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey("cartoes.id"), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)  # UUID do Cosmos
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    dt_pedido = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "card_id": self.card_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "dt_pedido": self.dt_pedido.strftime("%d/%m/%Y %H:%M")
        }
