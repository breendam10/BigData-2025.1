import requests
from bot.utils import API_BASE

class CompraDialog:
    async def run(self, turn_context, state, text):
        stage = state["stage"]
        dados = state["dados"]

        # Etapa 1: Pergunta ID do usuário
        if stage == "compra_id_user":
            if not text.strip().isdigit():
                await turn_context.send_activity("Digite um ID de usuário válido (apenas números).")
                return
            dados["user_id"] = int(text.strip())
            state["stage"] = "compra_id_produto"
            await turn_context.send_activity("Qual o ID do produto?")
            return

        # Etapa 2: Pergunta ID do produto
        if stage == "compra_id_produto":
            if not text.strip():
                await turn_context.send_activity("Digite um ID de produto válido.")
                return
            dados["product_id"] = text.strip()
            state["stage"] = "compra_quantidade"
            await turn_context.send_activity("Qual a quantidade?")
            return

        # Etapa 3: Pergunta quantidade
        if stage == "compra_quantidade":
            try:
                quantidade = int(text.strip())
                if quantidade <= 0:
                    raise ValueError
                dados["quantity"] = quantidade
            except ValueError:
                await turn_context.send_activity("Digite uma quantidade válida (apenas números inteiros positivos).")
                return
            state["stage"] = "compra_cartao"
            await turn_context.send_activity("Qual o ID do cartão de crédito?")
            return

        # Etapa 4: Pergunta ID do cartão
        if stage == "compra_cartao":
            if not text.strip().isdigit():
                await turn_context.send_activity("Digite um ID de cartão válido (apenas números).")
                return
            dados["card_id"] = int(text.strip())
            await self.efetuar_compra(turn_context, dados)
            state["stage"] = None
            state["dados"] = {}
            return

        # Comando inicial para iniciar o fluxo de compra
        if "comprar" in text:
            state["stage"] = "compra_id_user"
            state["dados"] = {}
            await turn_context.send_activity("Qual o ID do usuário?")
            return

    async def efetuar_compra(self, turn_context, dados):
        try:
            payload = {
                "user_id": dados["user_id"],
                "product_id": dados["product_id"],
                "quantity": dados["quantity"],
                "card_id": dados["card_id"]
            }
            resp = requests.post(f"{API_BASE}/orders", json=payload)
            if resp.status_code == 201:
                msg = resp.json().get("message", "Pedido realizado com sucesso!")
                order = resp.json().get("order", {})
                resumo = (
                    f"{msg}\n"
                    f"Produto: {order.get('product_name')}\n"
                    f"Qtd: {order.get('quantity')}\n"
                    f"Total: R${order.get('total_price')}"
                )
                await turn_context.send_activity(resumo)
            else:
                erro = resp.json().get("error", "Erro ao realizar pedido.")
                await turn_context.send_activity(f"Erro ao realizar compra: {erro}")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao realizar compra: {str(e)}")
