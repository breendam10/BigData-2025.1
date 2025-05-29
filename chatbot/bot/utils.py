import re

API_BASE = "https://ecommerce-hpgrbvc3bccecgeh.centralus-01.azurewebsites.net"

def extract_id(pattern, text):
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None
