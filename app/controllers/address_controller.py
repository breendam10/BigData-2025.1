from flask_restx import Namespace, Resource, fields
from app.db.mysql_db import db
from flask import request
from app.models.address_model import Address

address_ns = Namespace("address", description="Operações relacionadas a endereços")

address_model = address_ns.model("AddressModel", {
    "logradouro": fields.String(required=True, description="Logradouro"),
    "complemento": fields.String(required=False, description="Complemento"),
    "bairro": fields.String(required=False, description="Bairro"),
    "cidade": fields.String(required=True, description="Cidade"),
    "estado": fields.String(required=True, description="Estado"),
    "cep": fields.String(required=True, description="CEP")
})

@address_ns.route("/<int:user_id>")
class AddressList(Resource):
    @address_ns.expect(address_model, validate=True)
    @address_ns.response(201, "Endereço criado com sucesso")
    @address_ns.response(400, "Erro ao criar endereço")
    def post(self, user_id):
        """Cria um endereço para o usuário informado."""
        data = address_ns.payload
        try:
            new_address = Address(
                user_id=user_id,
                logradouro=data["logradouro"],
                complemento=data.get("complemento", ""),
                bairro=data.get("bairro", ""),
                cidade=data["cidade"],
                estado=data["estado"],
                cep=data["cep"]
            )
            db.session.add(new_address)
            db.session.commit()
            return {
                "message": "Endereço criado com sucesso",
                "address": new_address.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

@address_ns.route("/<int:user_id>/<int:address_id>")
class AddressResource(Resource):
    @address_ns.response(200, "Sucesso")
    @address_ns.response(404, "Endereço não encontrado")
    def get(self, user_id, address_id):
        """Retorna um endereço pelo ID e usuário."""
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        if not address:
            return {"error": "Endereço não encontrado"}, 404
        return {"address": address.to_dict()}, 200

    @address_ns.response(204, "Endereço deletado com sucesso")
    @address_ns.response(404, "Endereço não encontrado")
    def delete(self, user_id, address_id):
        """Deleta um endereço específico de um usuário."""
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        if not address:
            return {"error": "Endereço não encontrado"}, 404
        db.session.delete(address)
        db.session.commit()
        return "", 204
