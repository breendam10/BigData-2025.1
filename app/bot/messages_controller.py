# app/bot/messages_controller.py

from flask import Blueprint, request, jsonify, current_app
from botbuilder.schema import Activity
from app.bot.adapter import adapter
from app.bot.bot import Bot
import asyncio

bp = Blueprint("bot_messages", __name__, url_prefix="/api/messages")
bot = Bot()

@bp.route("", methods=["POST"])
def messages():
    if "application/json" in request.headers.get("Content-Type", ""):
        body = request.json
    else:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def aux_func(turn_context):
        await bot.on_turn(turn_context)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task = loop.create_task(adapter.process_activity(activity, auth_header, aux_func))
    try:
        loop.run_until_complete(task)
    finally:
        loop.close()
    return "", 202
