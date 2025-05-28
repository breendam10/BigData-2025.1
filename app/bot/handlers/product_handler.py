# app/bot/handlers/product_handler.py
from app.db.cosmos_db import get_cosmos_container
import uuid

async def handle_product_command(turn_context, text):
    container = get_cosmos_container()

    if "listar" in text:
        # Lista todos os produtos
        try:
            produtos = list(container.read_all_items())
            if not produtos:
                await turn_context.send_activity("Nenhum produto encontrado.")
                return
            lista = "\n".join([f"{p['id']}: {p.get('productName','')} - R${p.get('price','')}" for p in produtos])
            await turn_context.send_activity(f"Produtos cadastrados:\n{lista}")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao listar produtos: {str(e)}")

    elif "criar" in text:
        # Exemplo: produto criar nome=Mouse categoria=Periférico preco=99.99
        try:
            partes = text.replace("produto criar", "").strip().split()
            info = {kv.split("=")[0]: kv.split("=")[1] for kv in partes if "=" in kv}
            name = info.get("nome")
            cat = info.get("categoria") or info.get("category")
            preco = info.get("preco") or info.get("price")
            if not (name and cat and preco):
                await turn_context.send_activity("Forneça nome, categoria e preco. Exemplo: produto criar nome=Mouse categoria=Periférico preco=99.99")
                return

            product_id = str(uuid.uuid4())
            product_doc = {
                "id": product_id,
                "productCategory": cat,
                "productName": name,
                "price": float(preco),
                "imageUrl": [],  # Pode expandir se quiser
                "productDescription": info.get("descricao", "")
            }
            container.create_item(body=product_doc)
            await turn_context.send_activity(f"Produto criado: {name} (id {product_id})")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao criar produto: {str(e)}")

    elif "consultar" in text:
        # Exemplo: produto consultar id=abc123
        try:
            partes = text.split()
            idpart = next((p for p in partes if p.startswith("id=")), None)
            if not idpart:
                await turn_context.send_activity("Informe o id. Exemplo: produto consultar id=...")
                return
            pid = idpart.split("=")[1]
            produto = container.read_item(item=pid, partition_key=pid)
            await turn_context.send_activity(f"Produto: {produto['productName']} - R${produto['price']}\nDescrição: {produto.get('productDescription','')}")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar produto: {str(e)}")

    elif "deletar" in text:
        # Exemplo: produto deletar id=abc123
        try:
            partes = text.split()
            idpart = next((p for p in partes if p.startswith("id=")), None)
            if not idpart:
                await turn_context.send_activity("Informe o id. Exemplo: produto deletar id=...")
                return
            pid = idpart.split("=")[1]
            container.delete_item(item=pid, partition_key=pid)
            await turn_context.send_activity(f"Produto {pid} deletado.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao deletar produto: {str(e)}")

    else:
        await turn_context.send_activity("Comando de produto não reconhecido. Use: listar, criar, consultar, deletar.")
