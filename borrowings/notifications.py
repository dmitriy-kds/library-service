import os
import requests

from dotenv import load_dotenv

from users.models import User

load_dotenv()

TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")
URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def notify_borrowing_created(user: User, validated_data: dict) -> None:
    text = (f"User: {user.email} "
            f"borrowed {validated_data["book"].title} by "
            f"{validated_data["expected_return_date"]};\n"
            f"{validated_data["book"].inventory} copies remain in inventory")
    try:
        requests.post(url=URL, data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print(f"Telegram notification failed: {e}")
