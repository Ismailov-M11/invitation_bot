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
