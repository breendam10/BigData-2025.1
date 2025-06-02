from bot.dialogs.pedido_dialog import PedidoDialog
from bot.dialogs.produto_dialog import ProdutoDialog
from bot.dialogs.extrato_dialog import ExtratoDialog
from bot.dialogs.compra_dialog import CompraDialog
from botbuilder.schema import HeroCard, CardAction, ActionTypes, Attachment, Activity

class EcommerceBot:
    def __init__(self):
        self.user_state = {}
        self.pedido_dialog = PedidoDialog()
        self.produto_dialog = ProdutoDialog()
        self.extrato_dialog = ExtratoDialog()
        self.compra_dialog = CompraDialog()

    async def on_turn(self, turn_context):
        text = (turn_context.activity.text or "").strip().lower()
        user_id = turn_context.activity.from_property.id
        state = self.user_state.setdefault(user_id, {"stage": None, "dados": {}})
        stage = state["stage"] or ""

        # 1. PRIORIZE o dialog em andamento pelo stage!
        if stage.startswith("compra_"):
            await self.compra_dialog.run(turn_context, state, text)
        elif stage.startswith("pedido_"):
            await self.pedido_dialog.run(turn_context, state, text)
        elif stage.startswith("extrato_"):
            await self.extrato_dialog.run(turn_context, state, text)
        elif stage.startswith("produto_"):
            await self.produto_dialog.run(turn_context, state, text)
        else:
            # Só entra aqui se NENHUM dialog está em andamento!
            if "comprar" in text:
                await self.compra_dialog.run(turn_context, state, text)
            elif "pedido" in text:
                await self.pedido_dialog.run(turn_context, state, text)
            elif "produto" in text:
                await self.produto_dialog.run(turn_context, state, text)
            elif "extrato" in text:
                await self.extrato_dialog.run(turn_context, state, text)
            else:
                card = HeroCard(
                    title="Olá! O que você deseja fazer?",
                    buttons=[
                        CardAction(type=ActionTypes.im_back, title="Consultar produtos", value="produto"),
                        CardAction(type=ActionTypes.im_back, title="Listar pedidos", value="pedido"),
                        CardAction(type=ActionTypes.im_back, title="Gerar extrato", value="extrato"),
                    ]
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
