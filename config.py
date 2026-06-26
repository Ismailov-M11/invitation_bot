import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
DATABASE_URL: str = os.environ["DATABASE_URL"]
BASE_URL: str = os.getenv("BASE_URL", "https://your-invitation.com")

PASSWORD = "08.08.2026"
ENCODE_KEY = "w3dding_sh4hb0z_husn0r4_2026"

VERSIONS: dict[int, str] = {
    1: "🌅 Ertalabki tadbir (Osh)",
    2: "🌙 Kechki tadbir (Visol oqshomi)",
    3: "🎊 Ikki tadbir ham",
}
