# C:\Users\ianes\Desktop\BigData-2025.1\app\controllers\user_controller.py
from flask_restx import Namespace, Resource, fields
from flask import request
from datetime import datetime
from app.db.mysql_db import db
from app.models.user_model import User
from app.models.address_model import Address
from app.models.credit_card_model import CreditCard

user_ns = Namespace("users", description="Operações relacionadas a usuários")

user_model = user_ns.model("UserModel", {
    "nome": fields.String(required=True, description="Nome do usuário"),
    "email": fields.String(required=True, description="Email do usuário"),
    "dtNascimento": fields.String(required=False, description="Data de Nascimento (dd/mm/yyyy)", example="31/12/1990"),
    "cpf": fields.String(required=True, description="CPF do usuário"),
    "telefone": fields.String(required=False, description="Telefone do usuário")
})

@user_ns.route("")
class UserList(Resource):
    @user_ns.expect(user_model, validate=True)
    @user_ns.response(201, "Usuário criado com sucesso")
    @user_ns.response(400, "Erro ao criar usuário")
    def post(self):
        data = user_ns.payload
        try:
            nome = data["nome"]
            email = data["email"]
            cpf = data["cpf"]
            telefone = data.get("telefone")
            dt_str = data.get("dtNascimento")
            dt_nasc = None

            if dt_str:
                try:
                    dt_nasc = datetime.strptime(dt_str, "%d/%m/%Y").date()
                except ValueError:
                    return {"error": "Data de nascimento inválida. Use dd/mm/yyyy."}, 400

            new_user = User(
                nome=nome,
                email=email,
                dtNascimento=dt_nasc,
                cpf=cpf,
                telefone=telefone
            )
            db.session.add(new_user)
            db.session.commit()

            return {
                "message": "Usuário criado com sucesso",
                "user": new_user.to_dict()
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

@user_ns.route("/<int:user_id>")
class UserResource(Resource):
    @user_ns.response(200, "Sucesso")
    @user_ns.response(404, "Usuário não encontrado")
    def get(self, user_id):
        """Retorna um usuário pelo ID."""
        user = User.query.get(user_id)
        if not user:
            return {"error": "Usuário não encontrado"}, 404
        return {"user": user.to_dict()}, 200

    @user_ns.response(204, "Usuário deletado com sucesso")
    @user_ns.response(404, "Usuário não encontrado")
    def delete(self, user_id):
        """Deleta um usuário e todos os seus endereços e cartões."""
        user = User.query.get(user_id)
        if not user:
            return {"error": "Usuário não encontrado"}, 404
        Address.query.filter_by(user_id=user_id).delete()
        CreditCard.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        return "", 204
