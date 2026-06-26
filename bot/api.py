from aiohttp import web

from bot import database
from config import OWNER_CHAT_ID, OWNER_THREAD_ID, API_SECRET

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Secret",
}


async def _options(request: web.Request) -> web.Response:
    return web.Response(headers=CORS)


async def _card_copied(request: web.Request) -> web.Response:
    if request.headers.get("X-Secret") != API_SECRET:
        return web.json_response({"ok": False}, status=403, headers=CORS)

    try:
        data = await request.json()
        name      = (data.get("name")     or "").strip() or "—"
        amount    = (data.get("amount")   or "").strip()
        guest_uz  = (data.get("guest_uz") or "").strip()
        guest_ru  = (data.get("guest_ru") or "").strip()

        extra = f"amount:{amount}" if amount else "amount:—"
        if guest_uz:
            extra += f"|guest:{guest_uz}/{guest_ru}"

        await database.log_action(
            user_id=0,
            username=None,
            first_name=name,
            action="card_copied",
            extra=extra,
        )

        lines = ["💌 *Yangi to'yona niyati!*\n"]
        lines.append(f"👤 Ism: *{name}*")
        if amount:
            lines.append(f"💰 Miqdor: *{amount}*")
        if guest_uz:
            taklif = guest_uz + (f" / {guest_ru}" if guest_ru else "")
            lines.append(f"🎫 Taklif: {taklif}")
        lines.append("\n✅ Karta raqami nusxalandi")

        if OWNER_CHAT_ID:
            bot = request.app["bot"]
            await bot.send_message(
                OWNER_CHAT_ID,
                "\n".join(lines),
                parse_mode="Markdown",
                message_thread_id=OWNER_THREAD_ID,
            )

        return web.json_response({"ok": True}, headers=CORS)

    except Exception as e:
        return web.json_response({"ok": False, "error": str(e)}, status=500, headers=CORS)


def setup_app(app: web.Application) -> None:
    app.router.add_route("OPTIONS", "/api/card-copied", _options)
    app.router.add_post("/api/card-copied", _card_copied)
    app.router.add_get("/health", lambda r: web.json_response({"ok": True}))
