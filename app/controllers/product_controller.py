from flask_restx import Namespace, Resource, fields
from app.db.cosmos_db import get_cosmos_container
import uuid

product_ns = Namespace("products", description="Operações relacionadas a produtos (Cosmos DB)")

product_model = product_ns.model("ProductModel", {
    "productCategory": fields.String(required=True, description="Categoria do produto"),
    "productName": fields.String(required=True, description="Nome do produto"),
    "price": fields.Float(required=True, description="Preço do produto"),
    "imageUrl": fields.List(fields.String, required=True, description="URLs de imagem"),
    "productDescription": fields.String(required=False, description="Descrição do produto")
})

@product_ns.route("")
class ProductList(Resource):
    @product_ns.expect(product_model, validate=True)
    @product_ns.response(201, "Produto criado com sucesso")
    @product_ns.response(400, "Erro ao criar produto")
    def post(self):
        """Cria um produto no Cosmos DB."""
        data = product_ns.payload
        try:
            container = get_cosmos_container()  # Certifique-se de que você tem o container correto configurado.
            product_id = str(uuid.uuid4())  # Gerando o ID automaticamente como string
            product_doc = {
                "id": product_id,  # O ID será a chave de partição
                "productCategory": data["productCategory"],
                "productName": data["productName"],
                "price": data["price"],
                "imageUrl": data["imageUrl"],
                "productDescription": data.get("productDescription", "")
            }

            # Agora criamos o item com a chave de partição
            container.create_item(body=product_doc)  # Cria o item no Cosmos DB
            return {"message": "Produto criado com sucesso", "product": product_doc}, 201
        except Exception as e:
            return {"error": str(e)}, 400

@product_ns.route("/<string:product_id>")
class ProductResource(Resource):
    @product_ns.response(200, "Sucesso")
    @product_ns.response(404, "Produto não encontrado")
    def get(self, product_id):
        """Retorna um produto pelo ID."""
        container = get_cosmos_container()
        try:
            # Usando o ID como chave de partição
            product = container.read_item(item=product_id, partition_key=product_id)
            return {"product": product}, 200
        except Exception as e:
            return {"error": f"Produto não encontrado. Detalhes do erro: {str(e)}"}, 404

    @product_ns.response(204, "Produto deletado com sucesso")
    @product_ns.response(404, "Produto não encontrado")
    def delete(self, product_id):
        """Deleta um produto no Cosmos DB pelo seu ID."""
        container = get_cosmos_container()
        try:
            # Deletando o produto com o ID como chave de partição
            container.delete_item(item=product_id, partition_key=product_id)
            return "", 204
        except Exception as e:
            return {"error": f"Produto não encontrado. Detalhes do erro: {str(e)}"}, 404
