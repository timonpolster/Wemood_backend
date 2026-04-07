import asyncio
import logging
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from sqlalchemy import text
from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5
wait_seconds = 1

@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    """Prüft die Datenbankverbindung mit Retry-Logik bis die DB erreichbar ist."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(e)
        raise e

async def main() -> None:
    """Einstiegspunkt für den Pre-Start-Check vor dem Applikationsstart."""
    logger.info("Initializing service")
    await init()
    logger.info("Service finished initializing")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())