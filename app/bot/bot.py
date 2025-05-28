# app/bot/bot.py

from botbuilder.core import TurnContext
from app.bot.handlers.user_handler import handle_user_command
from app.bot.handlers.product_handler import handle_product_command
from app.bot.handlers.address_handler import handle_address_command
from app.bot.handlers.credit_card_handler import handle_credit_card_command

class Bot:
    async def on_turn(self, turn_context: TurnContext):
        text = (turn_context.activity.text or "").strip().lower()

        # Checa o tipo da mensagem
        if turn_context.activity.type == "message":
            # Decide para onde rotear de acordo com o comando inicial digitado
            if text.startswith("usuário") or text.startswith("usuario"):
                await handle_user_command(turn_context, text)
            elif text.startswith("produto"):
                await handle_product_command(turn_context, text)
            elif text.startswith("endereço") or text.startswith("endereco"):
                await handle_address_command(turn_context, text)
            elif text.startswith("cartão") or text.startswith("cartao"):
                await handle_credit_card_command(turn_context, text)
            else:
                await turn_context.send_activity(
                    "Comando não reconhecido. Use: usuário, produto, endereço ou cartão no início da mensagem."
                )
        else:
            await turn_context.send_activity(f"Evento do tipo {turn_context.activity.type} recebido.")
