# app/bot/handlers/address_handler.py
from app.models.address_model import Address
from app.db.mysql_db import db

async def handle_address_command(turn_context, text):
    if "listar" in text:
        # Exemplo: endereço listar user_id=1
        try:
            partes = text.split()
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not uid:
                await turn_context.send_activity("Informe o user_id. Exemplo: endereço listar user_id=1")
                return
            addresses = Address.query.filter_by(user_id=int(uid)).all()
            if not addresses:
                await turn_context.send_activity("Nenhum endereço encontrado para este usuário.")
                return
            lista = "\n".join([f"{a.id}: {a.logradouro}, {a.cidade} - {a.estado}" for a in addresses])
            await turn_context.send_activity(f"Endereços:\n{lista}")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao listar endereços: {str(e)}")

    elif "criar" in text:
        # Exemplo: endereço criar user_id=1 logradouro=RuaA cidade=Cidade estado=UF cep=12345
        try:
            partes = text.replace("endereço criar", "").replace("endereco criar", "").strip().split()
            info = {kv.split("=")[0]: kv.split("=")[1] for kv in partes if "=" in kv}
            user_id = info.get("user_id")
            logradouro = info.get("logradouro")
            cidade = info.get("cidade")
            estado = info.get("estado")
            cep = info.get("cep")
            complemento = info.get("complemento", "")
            bairro = info.get("bairro", "")
            if not (user_id and logradouro and cidade and estado and cep):
                await turn_context.send_activity(
                    "Informe user_id, logradouro, cidade, estado e cep. Exemplo: endereço criar user_id=1 logradouro=RuaA cidade=Cidade estado=UF cep=12345"
                )
                return
            novo = Address(
                user_id=int(user_id),
                logradouro=logradouro,
                complemento=complemento,
                bairro=bairro,
                cidade=cidade,
                estado=estado,
                cep=cep
            )
            db.session.add(novo)
            db.session.commit()
            await turn_context.send_activity(f"Endereço criado (id {novo.id}).")
        except Exception as e:
            db.session.rollback()
            await turn_context.send_activity(f"Erro ao criar endereço: {str(e)}")

    elif "consultar" in text:
        # Exemplo: endereço consultar id=1 user_id=1
        try:
            partes = text.split()
            aid = next((p.split("=")[1] for p in partes if p.startswith("id=")), None)
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not (aid and uid):
                await turn_context.send_activity("Informe id e user_id. Exemplo: endereço consultar id=2 user_id=1")
                return
            address = Address.query.filter_by(id=int(aid), user_id=int(uid)).first()
            if not address:
                await turn_context.send_activity("Endereço não encontrado.")
                return
            await turn_context.send_activity(
                f"Endereço: {address.logradouro}, {address.cidade} - {address.estado} (CEP: {address.cep})"
            )
        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar endereço: {str(e)}")

    elif "deletar" in text:
        # Exemplo: endereço deletar id=1 user_id=1
        try:
            partes = text.split()
            aid = next((p.split("=")[1] for p in partes if p.startswith("id=")), None)
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not (aid and uid):
                await turn_context.send_activity("Informe id e user_id. Exemplo: endereço deletar id=2 user_id=1")
                return
            address = Address.query.filter_by(id=int(aid), user_id=int(uid)).first()
            if not address:
                await turn_context.send_activity("Endereço não encontrado.")
                return
            db.session.delete(address)
            db.session.commit()
            await turn_context.send_activity(f"Endereço {aid} deletado.")
        except Exception as e:
            db.session.rollback()
            await turn_context.send_activity(f"Erro ao deletar endereço: {str(e)}")

    else:
        await turn_context.send_activity("Comando de endereço não reconhecido. Use: listar, criar, consultar, deletar.")
