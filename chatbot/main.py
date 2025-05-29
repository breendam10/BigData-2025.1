# C:\Users\ianes\Desktop\bot_app\main.py

import os
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from bot.core import EcommerceBot

APP_ID = os.environ.get("MICROSOFT_APP_ID", "")
APP_PASSWORD = os.environ.get("MICROSOFT_APP_PASSWORD", "")

adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

bot = EcommerceBot()

async def messages(req):
    auth_header = req.headers.get("Authorization", "")
    async def aux_func(turn_context):
        await bot.on_turn(turn_context)
    await adapter.process_activity(req, auth_header, aux_func)
    return web.Response(status=201)

app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    web.run_app(app, host="localhost", port=3978)
