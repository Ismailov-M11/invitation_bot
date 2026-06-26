import asyncpg

pool: asyncpg.Pool | None = None


async def init_db(dsn: str) -> None:
    global pool
    pool = await asyncpg.create_pool(dsn)
    await pool.execute("""
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
    await pool.execute(
        "INSERT INTO actions (user_id, username, first_name, action, extra) VALUES ($1,$2,$3,$4,$5)",
        user_id, username, first_name, action, extra,
    )


async def get_stats() -> list[asyncpg.Record]:
    return await pool.fetch(
        "SELECT action, COUNT(*) AS cnt FROM actions GROUP BY action ORDER BY cnt DESC"
    )


async def get_recent(limit: int = 8) -> list[asyncpg.Record]:
    return await pool.fetch(
        "SELECT first_name, username, action, extra, created_at FROM actions ORDER BY created_at DESC LIMIT $1",
        limit,
    )
