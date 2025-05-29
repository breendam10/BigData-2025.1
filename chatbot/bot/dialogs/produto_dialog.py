import re
import requests
from bot.utils import API_BASE

class ProdutoDialog:
    async def run(self, turn_context, state, text):
        stage = state["stage"]

        # 1. Consulta direta por ID
        match = re.search(r"(?:id=)?([a-f0-9\-]{10,})", text, re.IGNORECASE)
        if match:
            product_id = match.group(1)
            resp = requests.get(f"{API_BASE}/products/{product_id}")
            if resp.status_code == 200:
                produto = resp.json().get("product")
                if not produto:
                    await turn_context.send_activity("Produto não encontrado.")
                else:
                    msg = (
                        f"Produto encontrado:\n"
                        f"Nome: {produto['productName']}\n"
                        f"ID: {produto['id']}\n"
                        f"Preço: R${produto['price']}\n"
                        f"Categoria: {produto.get('productCategory', 'N/A')}\n"
                        f"Descrição: {produto.get('productDescription', 'N/A')}"
                    )
                    await turn_context.send_activity(msg)
            else:
                await turn_context.send_activity("Produto não encontrado.")
            state["stage"] = None
            return

        # 2. Diálogo listar/buscar
        if stage == "produto_listar_ou_buscar":
            if "listar" in text:
                await self.listar(turn_context)
                state["stage"] = None
            elif "buscar" in text:
                await turn_context.send_activity("Digite o nome do produto que deseja buscar:")
                state["stage"] = "produto_buscar_nome"
            else:
                await turn_context.send_activity(
                    "Digite 'listar' para ver todos ou 'buscar' para procurar por nome ou informe o ID do produto."
                )
            return

        if stage == "produto_buscar_nome":
            await self.buscar_nome(turn_context, text)
            state["stage"] = None
            return

        # 3. Comando inicial
        if text.strip() in ["produto", "produtos"]:
            await turn_context.send_activity(
                "Você quer listar todos os produtos ou buscar por nome? (Digite 'listar' ou 'buscar')"
            )
            state["stage"] = "produto_listar_ou_buscar"
            return

        # Fallback: lista todos
        await self.listar(turn_context)
        state["stage"] = None

    async def listar(self, turn_context):
        try:
            resp = requests.get(f"{API_BASE}/products/search?q=")
            if resp.status_code == 200:
                produtos = resp.json().get("results", [])
                if not produtos:
                    await turn_context.send_activity("Nenhum produto cadastrado.")
                    return
                msg = "\n".join(
                    [f"{p['productName']} (ID: {p['id']}), R${p['price']}" for p in produtos]
                )
                await turn_context.send_activity("Produtos disponíveis:\n" + msg)
            else:
                await turn_context.send_activity("Erro ao consultar produtos.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar produtos: {str(e)}")

    async def buscar_nome(self, turn_context, nome):
        try:
            resp = requests.get(f"{API_BASE}/products/search?q={nome.strip()}")
            if resp.status_code == 200:
                produtos = resp.json().get("results", [])
                if not produtos:
                    await turn_context.send_activity("Nenhum produto encontrado com esse nome.")
                    return
                msg = "\n".join(
                    [f"{p['productName']} (ID: {p['id']}), R${p['price']}" for p in produtos]
                )
                await turn_context.send_activity("Produtos encontrados:\n" + msg)
            else:
                await turn_context.send_activity("Erro ao consultar produtos.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar produtos: {str(e)}")
