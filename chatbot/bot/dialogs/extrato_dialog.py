import re
import requests
from bot.utils import API_BASE

class ExtratoDialog:
    async def run(self, turn_context, state, text):
        stage = state["stage"]

        # 1. Modo comando: ambos os IDs na mensagem
        m_user = re.search(r'id[_\s]?usu[aá]rio\s*=?\s*(\d+)', text)
        m_card = re.search(r'id[_\s]?cart[aã]o\s*=?\s*(\d+)', text)
        if m_user and m_card:
            user_id = m_user.group(1)
            card_id = m_card.group(1)
            await self.consultar_extrato(turn_context, user_id, card_id)
            state["stage"] = None
            return

        # 2. Diálogo: esperando user_id
        if stage == "extrato_id_user":
            state["dados"]["user_id"] = text.strip()
            state["stage"] = "extrato_id_card"
            await turn_context.send_activity("Qual o ID do cartão de crédito para consultar extrato?")
            return

        # 3. Diálogo: esperando card_id
        if stage == "extrato_id_card":
            user_id = state["dados"].get("user_id")
            card_id = text.strip()
            await self.consultar_extrato(turn_context, user_id, card_id)
            state["stage"] = None
            state["dados"] = {}
            return

        # 4. Comando inicial
        if "extrato" in text:
            await turn_context.send_activity("Qual o ID do usuário para consultar extrato?")
            state["stage"] = "extrato_id_user"
            return

    async def consultar_extrato(self, turn_context, user_id, card_id):
        try:
            resp = requests.get(f"{API_BASE}/orders/extract/{user_id}/{card_id}")
            if resp.status_code == 200:
                extrato = resp.json().get("extrato", [])
                if not extrato:
                    await turn_context.send_activity("Nenhuma compra encontrada para esse cartão/usuário.")
                    return
                msg = "\n".join([f"{p['product_name']}: R${p['total_price']} em {p['dt_pedido']}" for p in extrato])
                await turn_context.send_activity("Extrato:\n" + msg)
            else:
                await turn_context.send_activity("Erro ao buscar extrato.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao buscar extrato: {str(e)}")
