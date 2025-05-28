# app/bot/handlers/address_handler.py
import requests
from app.bot.adapter import API_URL

async def handle_address_command(turn_context, text):
    if "listar" in text:
        try:
            partes = text.split()
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not uid:
                await turn_context.send_activity("Informe o user_id. Exemplo: endereço listar user_id=1")
                return
            response = requests.get(f"{API_URL}/address/{uid}")
            if response.status_code == 200:
                addresses = response.json().get("addresses") or []
                if not addresses:
                    await turn_context.send_activity("Nenhum endereço encontrado para este usuário.")
                    return
                lista = "\n".join([f"{a['id']}: {a['logradouro']}, {a['cidade']} - {a['estado']}" for a in addresses])
                await turn_context.send_activity(f"Endereços:\n{lista}")
            else:
                await turn_context.send_activity("Erro ao listar endereços na API.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao listar endereços: {str(e)}")

    elif "criar" in text:
        try:
            partes = text.replace("endereço criar", "").replace("endereco criar", "").strip().split()
            info = {kv.split("=")[0]: kv.split("=")[1] for kv in partes if "=" in kv}
            user_id = info.get("user_id")
            data = {
                "logradouro": info.get("logradouro"),
                "complemento": info.get("complemento", ""),
                "bairro": info.get("bairro", ""),
                "cidade": info.get("cidade"),
                "estado": info.get("estado"),
                "cep": info.get("cep")
            }
            if not (user_id and data["logradouro"] and data["cidade"] and data["estado"] and data["cep"]):
                await turn_context.send_activity(
                    "Informe user_id, logradouro, cidade, estado e cep. Exemplo: endereço criar user_id=1 logradouro=RuaA cidade=Cidade estado=UF cep=12345"
                )
                return
            response = requests.post(f"{API_URL}/address/{user_id}", json=data)
            if response.status_code == 201:
                address = response.json().get("address", {})
                await turn_context.send_activity(f"Endereço criado (id {address.get('id', '?')}).")
            else:
                await turn_context.send_activity(f"Erro da API: {response.text}")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao criar endereço: {str(e)}")

    elif "consultar" in text:
        try:
            partes = text.split()
            aid = next((p.split("=")[1] for p in partes if p.startswith("id=")), None)
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not (aid and uid):
                await turn_context.send_activity("Informe id e user_id. Exemplo: endereço consultar id=2 user_id=1")
                return
            response = requests.get(f"{API_URL}/address/{uid}/{aid}")
            if response.status_code == 200:
                address = response.json().get("address", {})
                await turn_context.send_activity(
                    f"Endereço: {address['logradouro']}, {address['cidade']} - {address['estado']} (CEP: {address['cep']})"
                )
            else:
                await turn_context.send_activity("Endereço não encontrado.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar endereço: {str(e)}")

    elif "deletar" in text:
        try:
            partes = text.split()
            aid = next((p.split("=")[1] for p in partes if p.startswith("id=")), None)
            uid = next((p.split("=")[1] for p in partes if p.startswith("user_id=")), None)
            if not (aid and uid):
                await turn_context.send_activity("Informe id e user_id. Exemplo: endereço deletar id=2 user_id=1")
                return
            response = requests.delete(f"{API_URL}/address/{uid}/{aid}")
            if response.status_code == 204:
                await turn_context.send_activity(f"Endereço {aid} deletado.")
            else:
                await turn_context.send_activity("Endereço não encontrado ou erro ao deletar.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao deletar endereço: {str(e)}")

    else:
        await turn_context.send_activity("Comando de endereço não reconhecido. Use: listar, criar, consultar, deletar.")
