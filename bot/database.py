import asyncio
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

_dsn: str = ""


@contextmanager
def _conn():
    c = psycopg2.connect(_dsn)
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
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


async def init_db(dsn: str) -> None:
    global _dsn
    _dsn = dsn
    await asyncio.to_thread(_execute_sync, """
        CREATE TABLE IF NOT EXISTS actions (
            id         SERIAL PRIMARY KEY,
            user_id    BIGINT       NOT NULL,
            username   TEXT,
            first_name TEXT,
            action     TEXT         NOT NULL,
            extra      TEXT,
            created_at TIMESTAMPTZ  DEFAULT now()
        )
    """)


async def log_action(
    user_id: int,
    username: str | None,
    first_name: str | None,
    action: str,
    extra: str | None = None,
) -> None:
    await asyncio.to_thread(
        _execute_sync,
        "INSERT INTO actions (user_id, username, first_name, action, extra) VALUES (%s,%s,%s,%s,%s)",
        (user_id, username, first_name, action, extra),
    )


async def get_stats() -> list[dict]:
    return await asyncio.to_thread(
        _fetchall_sync,
        "SELECT action, COUNT(*) AS cnt FROM actions GROUP BY action ORDER BY cnt DESC",
    )


async def get_recent(limit: int = 8) -> list[dict]:
    return await asyncio.to_thread(
        _fetchall_sync,
        "SELECT first_name, username, action, extra, created_at FROM actions ORDER BY created_at DESC LIMIT %s",
        (limit,),
    )
