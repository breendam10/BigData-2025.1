# app/bot/handlers/credit_card_handler.py
import requests
from app.bot.adapter import API_URL

async def handle_credit_card_command(turn_context, text):
    if "listar" in text:
        try:
            partes = text.split()
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not uid:
                await turn_context.send_activity("Informe o user_id. Exemplo: cartão listar user_id=1")
                return
            response = requests.get(f"{API_URL}/credit_card/{uid}")
            if response.status_code == 200:
                cards = response.json().get("cards") or []
                if not cards:
                    await turn_context.send_activity("Nenhum cartão encontrado para este usuário.")
                    return
                lista = "\n".join([f"{c['id']}: final {c['numero'][-4:]}, saldo R${c['saldo']:.2f}, expira em {c['dtExpiracao']}" for c in cards])
                await turn_context.send_activity(f"Cartões encontrados:\n{lista}")
            else:
                await turn_context.send_activity("Erro ao listar cartões na API.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao listar cartões: {str(e)}")

    elif "criar" in text:
        from datetime import datetime
        try:
            partes = text.replace("cartão criar", "").replace("cartao criar", "").strip().split()
            info = {kv.split("=")[0]: kv.split("=")[1] for kv in partes if "=" in kv}
            user_id = info.get("user_id")
            data = {
                "numero": info.get("numero"),
                "dtExpiracao": info.get("dtExpiracao"),
                "cvv": info.get("cvv"),
                "saldo": float(info.get("saldo") or 0)
            }
            if not (user_id and data["numero"] and data["dtExpiracao"] and data["cvv"] and data["saldo"]):
                await turn_context.send_activity("Informe user_id, numero, dtExpiracao, cvv e saldo. Exemplo: cartão criar user_id=1 numero=123... dtExpiracao=10/2027 cvv=123 saldo=500.0")
                return
            response = requests.post(f"{API_URL}/credit_card/{user_id}", json=data)
            if response.status_code == 201:
                card = response.json().get("card", {})
                await turn_context.send_activity(f"Cartão criado (id {card.get('id', '?')}, final {card.get('numero','')[-4:]})")
            else:
                await turn_context.send_activity(f"Erro da API: {response.text}")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao criar cartão: {str(e)}")

    elif "consultar" in text:
        try:
            partes = text.split()
            cid = next((p.split("=")[1] for p in partes if p.startswith("id=")), None)
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not (cid and uid):
                await turn_context.send_activity("Informe id e user_id. Exemplo: cartão consultar id=2 user_id=1")
                return
            response = requests.get(f"{API_URL}/credit_card/{uid}/{cid}")
            if response.status_code == 200:
                card = response.json().get("card", {})
                await turn_context.send_activity(
                    f"Cartão id {card['id']}, final {card['numero'][-4:]}, saldo R${card['saldo']:.2f}, expira em {card['dtExpiracao']}"
                )
            else:
                await turn_context.send_activity("Cartão não encontrado.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar cartão: {str(e)}")

    elif "deletar" in text:
        try:
            partes = text.split()
            cid = next((p.split("=")[1] for p in partes if p.startswith("id=")), None)
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not (cid and uid):
                await turn_context.send_activity("Informe id e user_id. Exemplo: cartão deletar id=2 user_id=1")
                return
            response = requests.delete(f"{API_URL}/credit_card/{uid}/{cid}")
            if response.status_code == 204:
                await turn_context.send_activity(f"Cartão {cid} deletado.")
            else:
                await turn_context.send_activity("Cartão não encontrado ou erro ao deletar.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao deletar cartão: {str(e)}")

    else:
        await turn_context.send_activity("Comando de cartão não reconhecido. Use: listar, criar, consultar, deletar.")
