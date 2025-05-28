# app/bot/adapter.py

import os
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings

adapter_settings = BotFrameworkAdapterSettings(
    app_id=os.environ.get("MICROSOFT_APP_ID"),
    app_password=os.environ.get("MICROSOFT_APP_PASSWORD")
)
adapter = BotFrameworkAdapter(adapter_settings)
