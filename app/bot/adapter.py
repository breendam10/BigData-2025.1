# app/bot/adapter.py

import os
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings

# Config do Bot Framework
API_URL = "https://ecommerce-hpgrbvc3bccecgeh.centralus-01.azurewebsites.net"

adapter_settings = BotFrameworkAdapterSettings(
    app_id=os.environ.get("MICROSOFT_APP_ID", ""),
    app_password=os.environ.get("MICROSOFT_APP_PASSWORD", "")
)
adapter = BotFrameworkAdapter(adapter_settings)
