# app/bot/handlers/user_handler.py
from app.models.user_model import User
from app.db.mysql_db import db

async def handle_user_command(turn_context, text):
    # Exemplo simples de parsing de comando
    if "listar" in text:
        # Lista todos os usuários cadastrados
        users = User.query.all()
        if not users:
            await turn_context.send_activity("Nenhum usuário encontrado.")
            return
        lista = "\n".join([f"{u.id}: {u.nome} ({u.email})" for u in users])
        await turn_context.send_activity(f"Usuários cadastrados:\n{lista}")

    elif "criar" in text:
        # Exemplo: usuário criar nome=João email=joao@exemplo.com cpf=12345678900
        try:
            partes = text.replace("usuário criar", "").replace("usuario criar", "").strip().split()
            info = {kv.split("=")[0]: kv.split("=")[1] for kv in partes if "=" in kv}
            nome = info.get("nome")
            email = info.get("email")
            cpf = info.get("cpf")
            telefone = info.get("telefone")
            if not (nome and email and cpf):
                await turn_context.send_activity("Forneça nome, email e cpf. Exemplo: usuário criar nome=João email=joao@exemplo.com cpf=12345678900")
                return

            new_user = User(nome=nome, email=email, dtNascimento=None, cpf=cpf, telefone=telefone)
            db.session.add(new_user)
            db.session.commit()
            await turn_context.send_activity(f"Usuário criado: {new_user.nome} (id {new_user.id})")

        except Exception as e:
            db.session.rollback()
            await turn_context.send_activity(f"Erro ao criar usuário: {str(e)}")

    elif "consultar" in text:
        # Exemplo: usuário consultar id=1
        try:
            partes = text.split()
            idpart = next((p for p in partes if p.startswith("id=")), None)
            if not idpart:
                await turn_context.send_activity("Informe o id. Exemplo: usuário consultar id=1")
                return
            user_id = int(idpart.split("=")[1])
            user = User.query.get(user_id)
            if not user:
                await turn_context.send_activity("Usuário não encontrado.")
                return
            await turn_context.send_activity(f"Usuário {user.id}: {user.nome}, email: {user.email}")

        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar usuário: {str(e)}")

    elif "deletar" in text:
        # Exemplo: usuário deletar id=1
        try:
            partes = text.split()
            idpart = next((p for p in partes if p.startswith("id=")), None)
            if not idpart:
                await turn_context.send_activity("Informe o id. Exemplo: usuário deletar id=1")
                return
            user_id = int(idpart.split("=")[1])
            user = User.query.get(user_id)
            if not user:
                await turn_context.send_activity("Usuário não encontrado.")
                return
            db.session.delete(user)
            db.session.commit()
            await turn_context.send_activity(f"Usuário {user_id} deletado.")
        except Exception as e:
            db.session.rollback()
            await turn_context.send_activity(f"Erro ao deletar usuário: {str(e)}")

    else:
        await turn_context.send_activity("Comando de usuário não reconhecido. Use: listar, criar, consultar, deletar.")
