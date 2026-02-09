import httpx
from ..utils.logger import get_logger

logger = get_logger(__name__)

# change port depending on the other app
# local
# OTHER_APP_BASE_URL = "http://localhost:8000"

# host
OTHER_APP_BASE_URL = "http://151.185.41.194:8000"


async def sync_retailer(action: str, data: dict):
    """
    action: create | update | delete | register
    """
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(
                f"{OTHER_APP_BASE_URL}/internal/retailers/sync",
                json={
                    "action": action,
                    "data": data
                }
            )
    except Exception as e:
        logger.error(f"Retailer sync failed: {e}")
