# app/bot/handlers/user_handler.py

import requests
from app.bot.adapter import API_URL

async def handle_user_command(turn_context, text):
    if "listar" in text:
        try:
            response = requests.get(f"{API_URL}/users")
            if response.status_code == 200:
                data = response.json()
                users = data.get("users") or [data.get("user")] or []
                if not users or users == [None]:
                    await turn_context.send_activity("Nenhum usuário encontrado.")
                    return
                if isinstance(users, dict):
                    users = [users]
                lista = "\n".join([f"{u['id']}: {u['nome']} ({u['email']})" for u in users if u])
                await turn_context.send_activity(f"Usuários cadastrados:\n{lista}")
            else:
                await turn_context.send_activity("Erro ao listar usuários na API.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao listar usuários: {str(e)}")

    elif "criar" in text:
        try:
            partes = text.replace("usuário criar", "").replace("usuario criar", "").strip().split()
            info = {kv.split("=")[0]: kv.split("=")[1] for kv in partes if "=" in kv}
            data = {
                "nome": info.get("nome"),
                "email": info.get("email"),
                "cpf": info.get("cpf"),
                "telefone": info.get("telefone")
            }
            if not (data["nome"] and data["email"] and data["cpf"]):
                await turn_context.send_activity("Forneça nome, email e cpf. Exemplo: usuário criar nome=João email=joao@exemplo.com cpf=12345678900")
                return
            response = requests.post(f"{API_URL}/users", json=data)
            if response.status_code == 201:
                user = response.json().get("user", {})
                await turn_context.send_activity(f"Usuário criado: {user.get('nome', 'N/A')} (id {user.get('id', '?')})")
            else:
                await turn_context.send_activity(f"Erro da API: {response.text}")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao criar usuário: {str(e)}")

    elif "consultar" in text:
        try:
            partes = text.split()
            idpart = next((p for p in partes if p.startswith("id=")), None)
            if not idpart:
                await turn_context.send_activity("Informe o id. Exemplo: usuário consultar id=1")
                return
            user_id = idpart.split("=")[1]
            response = requests.get(f"{API_URL}/users/{user_id}")
            if response.status_code == 200:
                user = response.json().get("user", {})
                await turn_context.send_activity(f"Usuário {user['id']}: {user['nome']}, email: {user['email']}")
            else:
                await turn_context.send_activity("Usuário não encontrado.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar usuário: {str(e)}")

    elif "deletar" in text:
        try:
            partes = text.split()
            idpart = next((p for p in partes if p.startswith("id=")), None)
            if not idpart:
                await turn_context.send_activity("Informe o id. Exemplo: usuário deletar id=1")
                return
            user_id = idpart.split("=")[1]
            response = requests.delete(f"{API_URL}/users/{user_id}")
            if response.status_code == 204:
                await turn_context.send_activity(f"Usuário {user_id} deletado.")
            else:
                await turn_context.send_activity("Usuário não encontrado ou erro ao deletar.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao deletar usuário: {str(e)}")

    else:
        await turn_context.send_activity("Comando de usuário não reconhecido. Use: listar, criar, consultar, deletar.")
