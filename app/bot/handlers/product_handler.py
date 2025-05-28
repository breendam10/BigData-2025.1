# app/bot/handlers/product_handler.py
import requests
from app.bot.adapter import API_URL

async def handle_product_command(turn_context, text):
    if "listar" in text:
        try:
            response = requests.get(f"{API_URL}/products")
            if response.status_code == 200:
                produtos = response.json().get("products") or []
                if not produtos:
                    await turn_context.send_activity("Nenhum produto encontrado.")
                    return
                lista = "\n".join([f"{p['id']}: {p.get('productName','')} - R${p.get('price','')}" for p in produtos])
                await turn_context.send_activity(f"Produtos cadastrados:\n{lista}")
            else:
                await turn_context.send_activity("Erro ao listar produtos na API.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao listar produtos: {str(e)}")

    elif "criar" in text:
        try:
            partes = text.replace("produto criar", "").strip().split()
            info = {kv.split("=")[0]: kv.split("=")[1] for kv in partes if "=" in kv}
            data = {
                "productCategory": info.get("categoria") or info.get("category"),
                "productName": info.get("nome"),
                "price": float(info.get("preco") or info.get("price") or 0),
                "imageUrl": [],
                "productDescription": info.get("descricao", "")
            }
            if not (data["productCategory"] and data["productName"] and data["price"]):
                await turn_context.send_activity("Forneça nome, categoria e preco. Exemplo: produto criar nome=Mouse categoria=Periférico preco=99.99")
                return
            response = requests.post(f"{API_URL}/products", json=data)
            if response.status_code == 201:
                produto = response.json().get("product", {})
                await turn_context.send_activity(f"Produto criado: {produto.get('productName','N/A')} (id {produto.get('id','?')})")
            else:
                await turn_context.send_activity(f"Erro da API: {response.text}")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao criar produto: {str(e)}")

    elif "consultar" in text:
        try:
            partes = text.split()
            idpart = next((p for p in partes if p.startswith("id=")), None)
            if not idpart:
                await turn_context.send_activity("Informe o id. Exemplo: produto consultar id=...")
                return
            pid = idpart.split("=")[1]
            response = requests.get(f"{API_URL}/products/{pid}")
            if response.status_code == 200:
                produto = response.json().get("product", {})
                await turn_context.send_activity(f"Produto: {produto['productName']} - R${produto['price']}\nDescrição: {produto.get('productDescription','')}")
            else:
                await turn_context.send_activity("Produto não encontrado.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar produto: {str(e)}")

    elif "deletar" in text:
        try:
            partes = text.split()
            idpart = next((p for p in partes if p.startswith("id=")), None)
            if not idpart:
                await turn_context.send_activity("Informe o id. Exemplo: produto deletar id=...")
                return
            pid = idpart.split("=")[1]
            response = requests.delete(f"{API_URL}/products/{pid}")
            if response.status_code == 204:
                await turn_context.send_activity(f"Produto {pid} deletado.")
            else:
                await turn_context.send_activity("Produto não encontrado ou erro ao deletar.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao deletar produto: {str(e)}")

    else:
        await turn_context.send_activity("Comando de produto não reconhecido. Use: listar, criar, consultar, deletar.")
