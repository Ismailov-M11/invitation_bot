import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
DATABASE_URL: str = os.environ["DATABASE_URL"]
BASE_URL: str = os.getenv("BASE_URL", "https://your-invitation.com")
OWNER_CHAT_ID: int = int(os.getenv("OWNER_CHAT_ID", "0"))
OWNER_THREAD_ID: int | None = int(v) if (v := os.getenv("OWNER_THREAD_ID")) else None
API_SECRET: str = os.getenv("API_SECRET", "secret_08082026")
PORT: int = int(os.getenv("PORT", "8080"))

PASSWORD = "08.08.2026"
ENCODE_KEY = "w3dding_sh4hb0z_husn0r4_2026"

VERSIONS: dict[int, str] = {
    1: "🌅 Ertalabki tadbir (Osh)",
    2: "🌙 Kechki tadbir (Visol oqshomi)",
    3: "🎊 Ikki tadbir ham",
}
