import re
import requests
from bot.utils import API_BASE
from botbuilder.schema import HeroCard, CardImage, CardAction, ActionTypes, Attachment, Activity

class ProdutoDialog:
    async def run(self, turn_context, state, text):
        stage = state["stage"]

        # 1. Consulta direta por ID
        match = re.search(r"(?:id=)?([a-f0-9\-]{10,})", text, re.IGNORECASE)
        if match:
            product_id = match.group(1)
            resp = requests.get(f"{API_BASE}/products/{product_id}")
            if resp.status_code == 200:
                produto = resp.json().get("product")
                if not produto:
                    await turn_context.send_activity("Produto não encontrado.")
                else:
                    # Cria um Hero Card com imagem, campos e descrição
                    card = HeroCard(
                        title=produto.get('productName', 'Produto'),
                        subtitle=f"Categoria: {produto.get('productCategory', 'N/A')}",
                        text=f"Preço: R${produto.get('price', 'N/A')}\n\n{produto.get('productDescription', '')}",
                        images=[CardImage(url=produto.get('imageUrl', [''])[0])] if produto.get('imageUrl') else [],
                        buttons=[
                            CardAction(
                                type=ActionTypes.im_back,
                                title="Comprar",
                                value=f"comprar id_produto={p['id']}"
                            )
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
            else:
                await turn_context.send_activity("Produto não encontrado.")
            state["stage"] = None
            return

        # 2. Diálogo listar/buscar
        if stage == "produto_listar_ou_buscar":
            if "listar" in text:
                await self.listar(turn_context)
                state["stage"] = None
            elif "buscar" in text:
                await turn_context.send_activity("Digite o nome do produto que deseja buscar:")
                state["stage"] = "produto_buscar_nome"
            else:
                await turn_context.send_activity(
                    "Digite 'listar' para ver todos ou 'buscar' para procurar por nome ou informe o ID do produto."
                )
            return

        if stage == "produto_buscar_nome":
            await self.buscar_nome(turn_context, text)
            state["stage"] = None
            return

        # 3. Comando inicial
        if text.strip() in ["produto", "produtos"]:
            card = HeroCard(
                title="Consulta de produtos",
                text="Se você já sabe o ID, é só digitá-lo.\n\nOu escolha uma opção:",
                buttons=[
                    CardAction(type=ActionTypes.im_back, title="Listar todos", value="listar"),
                    CardAction(type=ActionTypes.im_back, title="Buscar por nome", value="buscar"),
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
            state["stage"] = "produto_listar_ou_buscar"
            return


        # Fallback: lista todos
        await self.listar(turn_context)
        state["stage"] = None

    async def listar(self, turn_context):
        try:
            resp = requests.get(f"{API_BASE}/products/search?q=")
            if resp.status_code == 200:
                produtos = resp.json().get("results", [])
                if not produtos:
                    await turn_context.send_activity("Nenhum produto cadastrado.")
                    return

                attachments = []
                for p in produtos:
                    card = HeroCard(
                        title=p.get('productName', 'Produto'),
                        subtitle=f"Categoria: {p.get('productCategory', 'N/A')}",
                        text=f"Preço: R${p.get('price', 'N/A')}\n\n{p.get('productDescription', '')}",
                        images=[CardImage(url=p.get('imageUrl', [''])[0])] if p.get('imageUrl') else [],
                        buttons=[
                            CardAction(
                                type=ActionTypes.im_back,
                                title="Comprar",
                                value=f"comprar id_produto={p['id']}"
                            )
                        ]
                    )
                    attachments.append(
                        Attachment(
                            content_type="application/vnd.microsoft.card.hero",
                            content=card
                        )
                    )
                # Envia todos os cards juntos como um carrossel (ou separadamente, se preferir)
                await turn_context.send_activity(
                    Activity(
                        type="message",
                        attachments=attachments,
                        attachment_layout="carousel" if len(attachments) > 1 else None
                    )
                )
            else:
                await turn_context.send_activity("Erro ao consultar produtos.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar produtos: {str(e)}")

    async def buscar_nome(self, turn_context, nome):
        try:
            resp = requests.get(f"{API_BASE}/products/search?q={nome.strip()}")
            if resp.status_code == 200:
                produtos = resp.json().get("results", [])
                if not produtos:
                    await turn_context.send_activity("Nenhum produto encontrado com esse nome.")
                    return

                attachments = []
                for p in produtos:
                    card = HeroCard(
                        title=p.get('productName', 'Produto'),
                        subtitle=f"Categoria: {p.get('productCategory', 'N/A')}",
                        text=f"Preço: R${p.get('price', 'N/A')}\n\n{p.get('productDescription', '')}",
                        images=[CardImage(url=p.get('imageUrl', [''])[0])] if p.get('imageUrl') else [],
                        buttons=[
                            CardAction(
                                type=ActionTypes.im_back,
                                title="Comprar",
                                value=f"comprar id_produto={p['id']}"
                            )
                        ]
                    )
                    attachments.append(
                        Attachment(
                            content_type="application/vnd.microsoft.card.hero",
                            content=card
                        )
                    )
                await turn_context.send_activity(
                    Activity(
                        type="message",
                        attachments=attachments,
                        attachment_layout="carousel" if len(attachments) > 1 else None
                    )
                )
            else:
                await turn_context.send_activity("Erro ao consultar produtos.")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao consultar produtos: {str(e)}")

