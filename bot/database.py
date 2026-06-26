import asyncio
import os
from contextlib import contextmanager
from urllib.parse import urlparse, unquote

import pg8000.dbapi

_params: dict = {}


def _build_params(dsn: str) -> dict:
    # Railway injects individual PG* vars — prefer them over URL parsing
    if os.getenv("PGUSER"):
        return {
            "host": os.environ["PGHOST"],
            "port": int(os.getenv("PGPORT", "5432")),
            "database": os.environ["PGDATABASE"],
            "user": os.environ["PGUSER"],
            "password": os.getenv("PGPASSWORD", ""),
        }
    # Fallback: parse DATABASE_URL
    u = urlparse(dsn)
    return {
        "host": u.hostname or "localhost",
        "port": u.port or 5432,
        "database": u.path.lstrip("/") or "postgres",
        "user": unquote(u.username) if u.username else None,
        "password": unquote(u.password) if u.password else "",
    }


@contextmanager
def _conn():
    c = pg8000.dbapi.connect(**_params)
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()


def _execute_sync(sql: str, params: tuple = ()) -> None:
    with _conn() as c:
        c.cursor().execute(sql, params)


def _fetchall_sync(sql: str, params: tuple = ()) -> list[dict]:
    with _conn() as c:
        cur = c.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


async def init_db(dsn: str) -> None:
    global _params
    _params = _build_params(dsn)
    await asyncio.to_thread(_execute_sync, """
        CREATE TABLE IF NOT EXISTS card_copies (
            id         SERIAL PRIMARY KEY,
            name       TEXT         NOT NULL,
            amount     TEXT,
            guest_uz   TEXT,
            guest_ru   TEXT,
            copied_at  TIMESTAMPTZ  DEFAULT now()
        )
    """)
    await asyncio.to_thread(_execute_sync, """
        CREATE TABLE IF NOT EXISTS authenticated_users (
            user_id    BIGINT PRIMARY KEY,
            username   TEXT,
            first_name TEXT,
            added_at   TIMESTAMPTZ DEFAULT now()
        )
    """)
    await asyncio.to_thread(_execute_sync, """
        CREATE TABLE IF NOT EXISTS notify_groups (
            chat_id    BIGINT  NOT NULL,
            thread_id  INT     NOT NULL DEFAULT 0,
            title      TEXT,
            added_at   TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (chat_id, thread_id)
        )
    """)



async def log_card_copy(
    name: str,
    amount: str | None = None,
    guest_uz: str | None = None,
    guest_ru: str | None = None,
) -> None:
    await asyncio.to_thread(
        _execute_sync,
        "INSERT INTO card_copies (name, amount, guest_uz, guest_ru) VALUES (%s,%s,%s,%s)",
        (name, amount or None, guest_uz or None, guest_ru or None),
    )


async def get_card_copies(limit: int = 50) -> list[dict]:
    return await asyncio.to_thread(
        _fetchall_sync,
        "SELECT name, amount, guest_uz, guest_ru, copied_at FROM card_copies ORDER BY copied_at DESC LIMIT %s",
        (limit,),
    )


async def add_auth_user(user_id: int, username: str | None, first_name: str | None) -> None:
    await asyncio.to_thread(
        _execute_sync,
        """INSERT INTO authenticated_users (user_id, username, first_name)
           VALUES (%s, %s, %s)
           ON CONFLICT (user_id) DO UPDATE
           SET username=EXCLUDED.username, first_name=EXCLUDED.first_name""",
        (user_id, username, first_name),
    )


async def get_auth_user_ids() -> list[int]:
    rows = await asyncio.to_thread(
        _fetchall_sync,
        "SELECT user_id FROM authenticated_users",
    )
    return [r["user_id"] for r in rows]


async def add_notify_group(chat_id: int, thread_id: int, title: str | None) -> None:
    await asyncio.to_thread(
        _execute_sync,
        """INSERT INTO notify_groups (chat_id, thread_id, title)
           VALUES (%s, %s, %s)
           ON CONFLICT (chat_id, thread_id) DO UPDATE SET title=EXCLUDED.title""",
        (chat_id, thread_id, title),
    )


async def get_notify_groups() -> list[dict]:
    return await asyncio.to_thread(
        _fetchall_sync,
        "SELECT chat_id, thread_id FROM notify_groups",
    )


