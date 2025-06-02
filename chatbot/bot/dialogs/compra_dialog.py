import re
import requests
from bot.utils import API_BASE
from botbuilder.schema import HeroCard, CardAction, ActionTypes, Attachment, Activity

class CompraDialog:
    async def run(self, turn_context, state, text):
        stage = state["stage"]
        dados = state["dados"]

        # 0. Se veio clique em botão de cartão (cartao_id=...)
        match_cartao = re.search(r"cartao_id\s*=\s*([a-f0-9\-]+)", text)
        if stage == "compra_cartao" and match_cartao:
            dados["card_id"] = match_cartao.group(1)
            await self.efetuar_compra(turn_context, dados)
            state["stage"] = None
            state["dados"] = {}
            return

        # Ao clicar em "Comprar" no produto, entra aqui:
        match = re.search(r"comprar\s+id_produto\s*=\s*([a-f0-9\-]+)", text)
        if match:
            product_id = match.group(1)
            state["dados"] = {"product_id": product_id}
            state["stage"] = "compra_id_user"
            await turn_context.send_activity("Qual o ID do usuário?")
            return

        # Etapa 1: Pergunta ID do usuário
        if stage == "compra_id_user":
            if not text.strip().isdigit():
                await turn_context.send_activity("Digite um ID de usuário válido (apenas números).")
                return
            dados["user_id"] = int(text.strip())
            # AJUSTE PRINCIPAL: só peça o produto SE não veio do botão comprar
            if "product_id" in dados:
                state["stage"] = "compra_quantidade"
                await turn_context.send_activity("Qual a quantidade?")
            else:
                state["stage"] = "compra_id_produto"
                await turn_context.send_activity("Qual o ID do produto?")
            return

        # Etapa 2: Pergunta ID do produto (só se ainda não tem)
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
            # Agora, mostra o Hero Card de cartões!
            state["stage"] = "compra_cartao"
            await self.mostrar_cartoes(turn_context, dados["user_id"], state)
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
                msg = resp.json().get("message", "✅ Pedido realizado com sucesso!")
                order = resp.json().get("order", {})
                resumo = (
                    f"{msg}\n\n"
                    f"Produto: {order.get('product_name')}\n\n"
                    f"Qtd: {order.get('quantity')}\n\n"
                    f"Total: R${order.get('total_price')}"
                )
                await turn_context.send_activity(resumo)
            else:
                erro = resp.json().get("error", "🛑Erro ao realizar pedido.")
                await turn_context.send_activity(f"🛑Erro ao realizar compra: {erro}")
        except Exception as e:
            await turn_context.send_activity(f"🛑Erro ao realizar compra: {str(e)}")

    async def mostrar_cartoes(self, turn_context, user_id, state):
        try:
            resp = requests.get(f"{API_BASE}/credit_card/{user_id}")
            if resp.status_code == 200:
                cartoes = resp.json().get("cartoes", [])
                if not cartoes:
                    await turn_context.send_activity("Nenhum cartão cadastrado para esse usuário.")
                    state["stage"] = None
                    state["dados"] = {}
                    return
                buttons = [
                    CardAction(
                        type=ActionTypes.im_back,
                        title=f"************{str(c['numero'])[-4:]}",
                        value=f"cartao_id={c['id']}"
                    )
                    for c in cartoes
                ]
                card = HeroCard(
                    title="Selecione um cartão",
                    text="Selecione um cartão cadastrado pelo usuário, considerando os 4 últimos dígitos:",
                    buttons=buttons
                )
                attachment = Attachment(
                    content_type="application/vnd.microsoft.card.hero",
                    content=card
                )
                await turn_context.send_activity(Activity(
                    type="message",
                    attachments=[attachment]
                ))
                # Espera o usuário clicar em um botão!
            else:
                await turn_context.send_activity("Erro ao buscar cartões do usuário.")
                state["stage"] = None
                state["dados"] = {}
        except Exception as e:
            await turn_context.send_activity(f"Erro ao buscar cartões: {str(e)}")
            state["stage"] = None
            state["dados"] = {}