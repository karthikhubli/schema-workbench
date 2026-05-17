import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def list_vendors():
    logger.info("Listing vendors")
    return ["Foxboro", "Honeywell"]
