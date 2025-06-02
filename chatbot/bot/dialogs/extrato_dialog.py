import re
import requests
from bot.utils import API_BASE
from botbuilder.schema import HeroCard, CardAction, ActionTypes, Attachment, Activity

class ExtratoDialog:
    MESES = [
        ("01", "Janeiro"), ("02", "Fevereiro"), ("03", "Março"), ("04", "Abril"),
        ("05", "Maio"), ("06", "Junho"), ("07", "Julho"), ("08", "Agosto"),
        ("09", "Setembro"), ("10", "Outubro"), ("11", "Novembro"), ("12", "Dezembro")
    ]

    async def run(self, turn_context, state, text):
        stage = state["stage"]

        # Modo comando: tudo na mensagem
        m_user = re.search(r'id[_\s]?usu[aá]rio\s*=?\s*(\d+)', text)
        m_card = re.search(r'id[_\s]?cart[aã]o\s*=?\s*(\d+)', text)
        m_mes = re.search(r'm[eê]s\s*=?\s*(\d{1,2})', text)
        if m_user and m_card and m_mes:
            user_id = m_user.group(1)
            card_id = m_card.group(1)
            mes = m_mes.group(1).zfill(2)
            await self.consultar_extrato(turn_context, user_id, card_id, mes)
            state["stage"] = None
            state["dados"] = {}
            return

        # Etapa: esperar id_usuario
        if stage == "extrato_id_user":
            state["dados"]["user_id"] = text.strip()
            # Busca os cartões do usuário e mostra os botões:
            state["stage"] = "extrato_id_card"
            await self.mostrar_cartoes(turn_context, state["dados"]["user_id"], state)
            return

        # Etapa: esperar clique no cartão
        match_cartao = re.search(r"cartao_id\s*=\s*([a-f0-9\-]+)", text)
        if stage == "extrato_id_card" and match_cartao:
            state["dados"]["card_id"] = match_cartao.group(1)
            # Agora pede o mês!
            state["stage"] = "extrato_mes"
            await self.enviar_hero_card_meses(turn_context)
            return

        # Etapa: esperar clique no mês
        if stage == "extrato_mes":
            user_id = state["dados"].get("user_id")
            card_id = state["dados"].get("card_id")
            mes = self.nome_mes_para_numero(text)
            if not mes:
                await turn_context.send_activity("Por favor, selecione um mês clicando em um dos botões.")
                return
            await self.consultar_extrato(turn_context, user_id, card_id, mes)
            state["stage"] = None
            state["dados"] = {}
            return

        # Comando inicial
        if "extrato" in text:
            await turn_context.send_activity("Qual o ID do usuário para consultar extrato?")
            state["stage"] = "extrato_id_user"
            return

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
            else:
                await turn_context.send_activity("Erro ao buscar cartões do usuário.")
                state["stage"] = None
                state["dados"] = {}
        except Exception as e:
            await turn_context.send_activity(f"Erro ao buscar cartões: {str(e)}")
            state["stage"] = None
            state["dados"] = {}


    async def enviar_hero_card_meses(self, turn_context):
        buttons = [
            CardAction(
                type=ActionTypes.im_back,
                title=nome,
                value=nome
            ) for cod, nome in self.MESES
        ]
        card = HeroCard(
            title="Selecione o mês do extrato:",
            buttons=buttons
        )
        attachment = Attachment(
            content_type="application/vnd.microsoft.card.hero",
            content=card
        )
        await turn_context.send_activity(
            Activity(
                type="message",
                attachments=[attachment]
            )
        )

    def nome_mes_para_numero(self, nome):
        nome = nome.strip().lower()
        for cod, extenso in self.MESES:
            if nome == extenso.lower():
                return cod
        return None

    async def consultar_extrato(self, turn_context, user_id, card_id, mes):
        try:
            resp = requests.get(f"{API_BASE}/orders/extract/{user_id}/{card_id}/{mes}")
            if resp.status_code == 200:
                extrato = resp.json().get("extrato", [])
                if not extrato:
                    await turn_context.send_activity("Nenhuma compra encontrada para esse cartão/usuário nesse mês.")
                    return
                msg = "\n\n".join([f"{p['product_name']}: R${p['total_price']} em {p['dt_pedido']}" for p in extrato])
                await turn_context.send_activity(f"Extrato do mês {mes}:\n\n" + msg)
            else:
                await turn_context.send_activity("Erro ao buscar extrato.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao buscar extrato: {str(e)}")
