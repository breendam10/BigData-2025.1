# app/bot/handlers/credit_card_handler.py
from app.models.credit_card_model import CreditCard
from app.db.mysql_db import db
from datetime import datetime

async def handle_credit_card_command(turn_context, text):
    if "listar" in text:
        # Exemplo: cartão listar user_id=1
        try:
            partes = text.split()
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not uid:
                await turn_context.send_activity("Informe o user_id. Exemplo: cartão listar user_id=1")
                return
            cards = CreditCard.query.filter_by(user_id=int(uid)).all()
            if not cards:
                await turn_context.send_activity("Nenhum cartão encontrado para este usuário.")
                return
            lista = "\n".join([f"{c.id}: final {c.numero[-4:]}, saldo R${c.saldo:.2f}, expira em {c.dtExpiracao.strftime('%m/%Y')}" for c in cards])
            await turn_context.send_activity(f"Cartões encontrados:\n{lista}")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao listar cartões: {str(e)}")

    elif "criar" in text:
        # Exemplo: cartão criar user_id=1 numero=1234567890123456 dtExpiracao=10/2030 cvv=123 saldo=500.0
        try:
            partes = text.replace("cartão criar", "").replace("cartao criar", "").strip().split()
            info = {kv.split("=")[0]: kv.split("=")[1] for kv in partes if "=" in kv}
            user_id = info.get("user_id")
            numero = info.get("numero")
            dt_exp = info.get("dtExpiracao")
            cvv = info.get("cvv")
            saldo = info.get("saldo")
            if not (user_id and numero and dt_exp and cvv and saldo):
                await turn_context.send_activity("Informe user_id, numero, dtExpiracao, cvv e saldo. Exemplo: cartão criar user_id=1 numero=123... dtExpiracao=10/2030 cvv=123 saldo=500.0")
                return

            # dtExpiracao pode ser "10/2030" ou "10/2025" ou "10/12/2025"
            try:
                if len(dt_exp.split("/")) == 2:
                    dtExpiracao = datetime.strptime(dt_exp, "%m/%Y").date()
                else:
                    dtExpiracao = datetime.strptime(dt_exp, "%d/%m/%Y").date()
            except:
                await turn_context.send_activity("Data de expiração inválida. Use mm/aaaa ou dd/mm/aaaa.")
                return

            new_card = CreditCard(
                user_id=int(user_id),
                numero=numero,
                dtExpiracao=dtExpiracao,
                cvv=cvv,
                saldo=float(saldo)
            )
            db.session.add(new_card)
            db.session.commit()
            await turn_context.send_activity(f"Cartão criado (id {new_card.id}, final {numero[-4:]})")
        except Exception as e:
            db.session.rollback()
            await turn_context.send_activity(f"Erro ao criar cartão: {str(e)}")

    elif "consultar" in text:
        # Exemplo: cartão consultar id=2 user_id=1
        try:
            partes = text.split()
            cid = next((p.split("=")[1] for p in partes if p.startswith("id=")), None)
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not (cid and uid):
                await turn_context.send_activity("Informe id e user_id. Exemplo: cartão consultar id=2 user_id=1")
                return
            card = CreditCard.query.filter_by(id=int(cid), user_id=int(uid)).first()
            if not card:
                await turn_context.send_activity("Cartão não encontrado.")
                return
            await turn_context.send_activity(
                f"Cartão id {card.id}, final {card.numero[-4:]}, saldo R${card.saldo:.2f}, expira em {card.dtExpiracao.strftime('%m/%Y')}"
            )
        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar cartão: {str(e)}")

    elif "deletar" in text:
        # Exemplo: cartão deletar id=2 user_id=1
        try:
            partes = text.split()
            cid = next((p.split("=")[1] for p in partes if p.startswith("id=")), None)
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not (cid and uid):
                await turn_context.send_activity("Informe id e user_id. Exemplo: cartão deletar id=2 user_id=1")
                return
            card = CreditCard.query.filter_by(id=int(cid), user_id=int(uid)).first()
            if not card:
                await turn_context.send_activity("Cartão não encontrado.")
                return
            db.session.delete(card)
            db.session.commit()
            await turn_context.send_activity(f"Cartão {cid} deletado.")
        except Exception as e:
            db.session.rollback()
            await turn_context.send_activity(f"Erro ao deletar cartão: {str(e)}")

    else:
        await turn_context.send_activity("Comando de cartão não reconhecido. Use: listar, criar, consultar, deletar.")
