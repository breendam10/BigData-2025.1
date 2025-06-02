import re
import requests
from bot.utils import API_BASE

class PedidoDialog:
    async def run(self, turn_context, state, text):
        stage = state["stage"]

        # 1. Consulta direta (modo comando) - user_id informado
        match = re.search(r'id[_\s]?usu[aá]rio\s*=?\s*(\d+)', text)
        if match:
            user_id = match.group(1)
            await self.consultar_pedidos(turn_context, user_id)
            state["stage"] = None
            return

        # 2. Modo diálogo (esperando id do usuário)
        if stage == "pedido_id_user":
            user_id = text.strip()
            await self.consultar_pedidos(turn_context, user_id)
            state["stage"] = None
            return

        # 3. Comando inicial
        if "pedido" in text:
            await turn_context.send_activity("Qual o ID do usuário para consultar pedidos?")
            state["stage"] = "pedido_id_user"
            return

    async def consultar_pedidos(self, turn_context, user_id):
        try:
            resp = requests.get(f"{API_BASE}/orders/{user_id}")
            if resp.status_code == 200:
                pedidos = resp.json().get("pedidos", [])
                if not pedidos:
                    await turn_context.send_activity("Nenhum pedido encontrado para este usuário.")
                    return
                msg = "\n\n".join([f"Pedido {p['id']}: {p['product_name']} (Qtd: {p['quantity']}) - R${p['total_price']}" for p in pedidos])
                await turn_context.send_activity("Pedidos encontrados:\n\n" + msg)
            else:
                await turn_context.send_activity("Erro ao buscar pedidos do usuário.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao buscar pedidos: {str(e)}")
